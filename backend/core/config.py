"""
全局配置管理
读取 .env 环境变量，提供统一配置入口
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent  # A21_final/
load_dotenv(BASE_DIR / ".env")

# 确保 data 目录存在
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)


class Settings:
    # 服务端口
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "a21password")

    # llama.cpp
    LLAMA_SERVER_URL: str = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8080")

    # Whisper
    WHISPER_SERVER_URL: str = os.getenv("WHISPER_SERVER_URL", "http://127.0.0.1:8081")

    # Chroma
    CHROMA_PERSIST_PATH: str = os.getenv("CHROMA_PERSIST_PATH", str(BASE_DIR / "data" / "chroma_db"))

    # SQLite
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", str(BASE_DIR / "data" / "feedbacks.db"))

    # Embedding
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-zh-v1.5")

    # 参数
    PARAMS_PATH: str = os.getenv("PARAMS_PATH", str(BASE_DIR / "rag" / "params.json"))


settings = Settings()
