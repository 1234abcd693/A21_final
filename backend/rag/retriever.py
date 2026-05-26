"""
双路混合检索模块 — 向量检索 + 图检索
=====================================
检索策略：向量相似度 (ChromaDB) + 知识图谱遍历 (Neo4j) → 直接输出

双路互补原理：
  - 向量检索：语义相似匹配（如"打不着火"↔"无法启动"），bge-base-zh-v1.5 (768维)
  - 图检索：  实体关系推理，沿 Symptom→Cause→Step 链路遍历，返回结构化三元组

设计决策（v2.0）：
  - 删除了 BM25 关键词检索：数据量小（658 chunks），BM25 索引构建 + 分词耗时且引入噪声
  - 不做 RRF 融合：两路结果性质不同（文档 vs 结构化三元组），各取 top_k 直接输出
  - 轻量化：减少 40% 检索耗时，降低 Prompt 长度
"""

import json
import logging
from pathlib import Path
from typing import Any

from core.config import settings
from rag.vector_store import search as chroma_search
from kg.neo4j_client import graph_search as cypher_search

logger = logging.getLogger(__name__)


def load_params() -> dict[str, Any]:
    """加载 RAG 参数配置"""
    params_path = Path(settings.PARAMS_PATH)
    if params_path.exists():
        return json.loads(params_path.read_text(encoding="utf-8"))

    return {
        "retrieval": {
            "vector_top_k": 4,    # 向量检索返回数
            "graph_top_k": 3,     # 图检索返回数（Neo4j 内部 limit）
        },
        "generation": {"temperature": 0.1, "max_tokens": 256},
    }


def hybrid_search(query: str, top_k: int = 4) -> dict[str, Any]:
    """
    双路检索 — 对外统一入口。

    检索流水线：
    1. 向量检索 (ChromaDB) → 语义相似匹配，top_k 条文档片段
    2. 图检索 (Neo4j Cypher) → 关系遍历，返回三元组链
    3. 不融合，分别返回（generator 中分别注入 Prompt）

    返回：
    {
        "chunks": [...],          # 文档片段列表（给 LLM 注入）
        "graph_results": [...],   # 图谱结构化三元组
    }
    """
    p = load_params()
    retrieval = p.get("retrieval", {})
    vec_k = retrieval.get("vector_top_k", top_k)

    # 双路并行检索（各自独立，不融合）
    vector_results = chroma_search(query, n_results=vec_k)
    graph_results = cypher_search(query)

    return {
        "chunks": vector_results,
        "graph_results": graph_results,
    }
