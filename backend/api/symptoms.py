"""
故障现象联想 + 知识图谱路由
"""

from typing import Optional

from fastapi import APIRouter, Query

from kg.neo4j_client import (
    get_symptoms,
    search_entities,
    get_node,
    expand_node,
    get_overview,
)

router = APIRouter()


# ===== 故障联想 =====

@router.get("/symptoms")
async def symptoms(
    keyword: str = Query("", description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50),
):
    """故障现象联想（输入框自动补全）"""
    items = get_symptoms(keyword=keyword, limit=limit)
    return {"symptoms": items}


# ===== 知识图谱 =====

@router.get("/graph/search")
async def graph_search(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50),
):
    """图谱搜索"""
    results = search_entities(query=q, limit=limit)
    return {"query": q, "results": results}


@router.get("/graph/node/{uid}")
async def graph_node(uid: str):
    """节点详情"""
    node = get_node(uid=uid)
    if node is None:
        return {"error": "节点不存在", "code": 404}
    return node


@router.get("/graph/expand/{uid}")
async def graph_expand(uid: str):
    """展开节点邻居"""
    result = expand_node(uid=uid)
    if not result.get("center"):
        return {"error": "节点不存在", "code": 404}
    return result


@router.get("/graph/overview")
async def graph_overview():
    """图谱全貌"""
    return get_overview()
