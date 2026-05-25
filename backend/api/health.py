"""
健康检查路由
"""

import time
from typing import Any

from fastapi import APIRouter

from kg.neo4j_client import check_connection as check_neo4j
from core.llm import _check_health as check_llama
from rag.vector_store import check_connection as check_chroma

router = APIRouter()
_start_time = time.time()


@router.get("/health")
async def health() -> dict[str, Any]:
    """系统健康检查"""
    neo4j_status = "connected" if check_neo4j() else "disconnected"
    llama_status = "connected" if await check_llama() else "disconnected"
    chroma_status = "connected" if check_chroma() else "disconnected"

    all_ok = all(s == "connected" for s in [neo4j_status, llama_status, chroma_status])

    return {
        "status": "ok" if all_ok else "degraded",
        "neo4j": neo4j_status,
        "llama": llama_status,
        "chroma": chroma_status,
        "uptime": int(time.time() - _start_time),
    }
