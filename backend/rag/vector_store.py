"""
Chroma 向量库初始化和操作

嵌入模型：bge-base-zh-v1.5（768维）
    - 写入：add_chunks() 需外部预计算 embedding 后调用 collection.add(embeddings=...)
    - 查询：search() 内部用 bge-base-zh-v1.5 编码查询文本，传 query_embeddings 给 ChromaDB
    - 为什么不用 ChromaDB 内置 embedding function：内置默认是 all-MiniLM-L6-v2（384维），
      与 bge 768维不兼容，会导致 "Embedding dimension 384 does not match 768" 错误。
"""

from typing import Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings

_client: Optional[Any] = None
_collection: Optional[Any] = None
_embedder: Optional[Any] = None  # bge-base-zh-v1.5 SentenceTransformer（惰性加载）


def _get_client() -> Any:
    """惰性初始化 Chroma 客户端"""
    global _client
    if _client is None:
        import os
        os.makedirs(settings.CHROMA_PERSIST_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def _get_embedder() -> Any:
    """惰性加载 bge-base-zh-v1.5 嵌入模型（768维），用于查询时编码。"""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder


def _get_collection() -> Any:
    """获取或创建 knowledge_chunks collection"""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name="knowledge_chunks",
            metadata={
                "description": "船舶故障诊断知识库",
                "embedding_model": settings.EMBEDDING_MODEL,
                "hnsw:space": "cosine",  # bge 用 L2 归一化 → 余弦距离
            },
        )
    return _collection


def check_connection() -> bool:
    """检查 Chroma 是否可用（heartbeat）"""
    try:
        _get_client().heartbeat()
        return True
    except Exception:
        return False


def add_chunks(
    ids: list[str],
    documents: list[str],
    metadatas: list[dict[str, Any]],
) -> None:
    """批量添加文档切片（需调用方预计算 embedding 并作为 embeddings= 参数传入）"""
    if not ids:
        return
    _get_collection().add(ids=ids, documents=documents, metadatas=metadatas)


def search(
    query: str,
    n_results: int = 5,
    where: Optional[dict] = None,
) -> list[dict[str, Any]]:
    """
    语义检索 — 用 bge-base-zh-v1.5 编码查询，传 query_embeddings 给 ChromaDB。

    返回 [{chunk_id, doc_name, page, text, score}, ...]
    """
    coll = _get_collection()

    # 用 bge-base-zh-v1.5 编码查询文本（768维），避免 ChromaDB 默认 384维 的不匹配
    embedder = _get_embedder()
    query_embedding = embedder.encode(query, normalize_embeddings=True).tolist()

    kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
    }
    if where:
        kwargs["where"] = where
    result = coll.query(**kwargs)

    output = []
    if result.get("ids") and result["ids"][0]:
        for i, chunk_id in enumerate(result["ids"][0]):
            meta = (result.get("metadatas", [[]])[0] or [{}])[i] or {}
            output.append({
                "chunk_id": chunk_id,
                "text": (result.get("documents", [[]])[0] or [""])[i],
                "score": (result.get("distances", [[]])[0] or [0])[i] if result.get("distances") else 0,
                "doc_name": meta.get("doc_name", ""),
                "page": meta.get("page", ""),
                "doc_type": meta.get("doc_type", ""),
                "graph_entities": meta.get("graph_entities", []),
            })
    return output


def get_collection_count() -> int:
    """获取 collection 中的文档数量"""
    try:
        return _get_collection().count()
    except Exception:
        return 0
