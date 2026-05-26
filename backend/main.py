"""
A21 船舶装备故障诊断智能问答系统 — FastAPI 入口

启动: uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""

import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router

# 配置全局日志（INFO 级别，输出到控制台）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库和预热模型"""
    logger.info("Initializing database...")
    from data.database import init_db
    init_db()
    logger.info("Warming up embedding model (first call ~5s on CPU)...")
    from rag.vector_store import _get_embedder
    embedder = _get_embedder()
    # 用一条假查询预热 ChromaDB + embedding pipeline
    _ = embedder.encode("预热", normalize_embeddings=True)
    from rag.vector_store import search as chroma_search
    _ = chroma_search("预热", n_results=1)
    logger.info("A21 backend ready (embedder warm, %d chunks)",
        _get_embedder().get_sentence_embedding_dimension()
        if hasattr(_get_embedder(), "get_sentence_embedding_dimension") else 0)
    yield


app = FastAPI(
    title="A21 船舶故障诊断系统",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
