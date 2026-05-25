"""
A21 船舶装备故障诊断智能问答系统 — FastAPI 入口

启动: uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api import router as api_router

app = FastAPI(
    title="A21 船舶故障诊断系统",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段全放通；打包后限制为 localhost
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
