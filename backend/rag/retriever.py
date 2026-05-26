"""
三路检索融合 (图检索 + BM25 + 向量) → RRF 排序
"""

import json
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

from core.config import settings
from rag.vector_store import search as chroma_search
from rag.entity_extractor import extract_keywords, extract_entities
from kg.neo4j_client import graph_search as cypher_search, search_entities as neo4j_link


# BM25 索引（内存中，从 Chroma 元数据构建）
_bm25_index: Any = None
_bm25_chunks: list[dict] = []


def _ensure_bm25_index():
    """惰性构建 BM25 索引"""
    global _bm25_index, _bm25_chunks
    if _bm25_index is not None:
        return
    # 从 Chroma 获取所有文档
    try:
        from rag.vector_store import _get_collection
        coll = _get_collection()
        result = coll.get()
        _bm25_chunks = []
        corpus = []
        for i, doc_id in enumerate(result.get("ids", [])):
            text = (result.get("documents", []) or [""])[i] or ""
            meta = (result.get("metadatas", []) or [{}])[i] or {}
            _bm25_chunks.append({"chunk_id": doc_id, "text": text, **meta})
            # jieba 分词作为 BM25 的 token
            import jieba
            corpus.append(list(jieba.cut(text)))
        if corpus:
            _bm25_index = BM25Okapi(corpus)
        else:
            _bm25_index = None  # 空库时设为 None
    except Exception:
        _bm25_index = None
        _bm25_chunks = []


def bm25_search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """BM25 关键词检索"""
    _ensure_bm25_index()
    if _bm25_index is None:
        return []
    import jieba
    tokens = list(jieba.cut(query))
    try:
        scores = _bm25_index.get_scores(tokens)
    except Exception:
        return []
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    results = []
    for idx, score in ranked:
        if idx < len(_bm25_chunks) and score > 0:
            results.append({**_bm25_chunks[idx], "score": float(score)})
    return results


def load_params() -> dict[str, Any]:
    """加载 RAG 参数配置"""
    params_path = Path(settings.PARAMS_PATH)
    if params_path.exists():
        return json.loads(params_path.read_text(encoding="utf-8"))
    return {
        "retrieval": {"alpha": 0.35, "beta": 0.35, "gamma": 0.3, "top_k_per_source": 5, "rerank_keep": 5},
        "generation": {"temperature": 0.1, "max_tokens": 512},
    }


def rrf_fuse(
    bm25_results: list[dict],
    vector_results: list[dict],
    graph_results: list[dict],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """
    RRF (Reciprocal Rank Fusion) 融合排序。
    不关心分数绝对值，只看排名。
    """
    scores: dict[str, float] = {}

    for rank, item in enumerate(bm25_results):
        cid = item.get("chunk_id", f"bm25_{rank}")
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)

    for rank, item in enumerate(vector_results):
        cid = item.get("chunk_id", f"vec_{rank}")
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)

    # 图检索结果（没有 chunk_id，用 graph_{rank} 标识）
    for rank, item in enumerate(graph_results):
        cid = f"graph_{rank}"
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)

    # 排序并取 top_k
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    fused = []
    for cid, score in ranked:
        # 找到对应的原始结果
        found = False
        for source, items in [("bm25", bm25_results), ("vector", vector_results), ("graph", graph_results)]:
            for i, item in enumerate(items):
                item_cid = item.get("chunk_id", f"graph_{i}")
                if item_cid == cid:
                    fused.append({**item, "fusion_score": score, "source": source})
                    found = True
                    break
            if found:
                break

    return fused


def hybrid_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """
    三路融合检索（对外统一入口）。
    返回: {chunks: [...], graph_results: [...]}
    """
    p = load_params()
    retrieval = p.get("retrieval", {})
    tk = retrieval.get("top_k_per_source", top_k)
    keep = retrieval.get("rerank_keep", top_k)

    # 1. 向量检索
    vector_results = chroma_search(query, n_results=tk)

    # 2. BM25 检索
    bm25_results = bm25_search(query, top_k=tk)

    # 3. 图检索
    graph_results = cypher_search(query)

    # 4. RRF 融合
    fused = rrf_fuse(bm25_results, vector_results, graph_results, top_k=keep)

    return {
        "chunks": [c for c in fused if c.get("source") != "graph"],
        "graph_results": graph_results,
        "all_results": fused,
    }
