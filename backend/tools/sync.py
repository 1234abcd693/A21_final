"""
U盘数据同步（导出/导入）
"""

import json
import logging
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from core.config import settings
from data.database import get_connection

logger = logging.getLogger(__name__)


def export_data(output_path: str) -> dict[str, Any]:
    """
    导出全库数据为 zip。
    通过 Neo4j APOC 导出 Cypher + 拷贝 Chroma + SQLite + params.json
    """
    export_dir = Path(output_path).parent / f"a21_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    export_dir.mkdir(parents=True, exist_ok=True)

    # 1. Neo4j Cypher 导出
    cypher_path = export_dir / "neo4j_dump.cypher"
    try:
        from kg.neo4j_client import _get_driver
        with _get_driver().session() as session:
            session.run(
                "CALL apoc.export.cypher.all($path, {format: 'cypher-shell'})",
                path=str(cypher_path),
            )
    except Exception as e:
        cypher_path.write_text(f"-- APOC export failed: {e}\n", encoding="utf-8")

    # 2. Chroma 拷贝
    chroma_src = Path(settings.CHROMA_PERSIST_PATH)
    chroma_dst = export_dir / "chroma_db"
    if chroma_src.exists():
        if chroma_dst.exists():
            shutil.rmtree(chroma_dst)
        shutil.copytree(chroma_src, chroma_dst)

    # 3. SQLite 拷贝
    sqlite_src = Path(settings.SQLITE_PATH)
    if sqlite_src.exists():
        shutil.copy(sqlite_src, export_dir / "feedbacks.db")

    # 4. params.json 拷贝
    params_src = Path(settings.PARAMS_PATH)
    if params_src.exists():
        shutil.copy(params_src, export_dir / "params.json")

    # 5. sync_info.json
    info = {
        "version": "1.0",
        "export_time": datetime.now().isoformat(),
        "embedding_model": settings.EMBEDDING_MODEL,
    }
    (export_dir / "sync_info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")

    # 6. 打包 zip
    zip_path = str(export_dir) + ".zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in export_dir.rglob("*"):
            if f.is_file():
                zf.write(f, f.relative_to(export_dir))

    shutil.rmtree(export_dir)
    return {"status": "ok", "path": zip_path}


def import_data(zip_path: str) -> dict[str, Any]:
    """
    导入知识包。
    校验 sync_info.json → MERGE Neo4j → 合并 Chroma → 合并 SQLite
    """
    extract_dir = Path(tempfile.mkdtemp())

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # 校验 sync_info
        info_path = extract_dir / "sync_info.json"
        sync_info = {}
        if info_path.exists():
            sync_info = json.loads(info_path.read_text(encoding="utf-8"))
            imported_model = sync_info.get("embedding_model", "")
            if imported_model and imported_model != settings.EMBEDDING_MODEL:
                return {
                    "status": "warning",
                    "model_mismatch": True,
                    "imported_model": imported_model,
                    "current_model": settings.EMBEDDING_MODEL,
                    "error": "embedding 模型不一致，向量可能无法使用",
                }

        # Neo4j 导入
        cypher_path = extract_dir / "neo4j_dump.cypher"
        cypher_imported = 0
        if cypher_path.exists():
            from kg.neo4j_client import _get_driver
            with _get_driver().session() as session:
                cypher_text = cypher_path.read_text(encoding="utf-8")
                for statement in cypher_text.split(";\n"):
                    statement = statement.strip()
                    if statement and not statement.startswith("//"):
                        try:
                            session.run(statement)
                            cypher_imported += 1
                        except Exception:
                            logger.exception("Cypher statement import failed: %s...", statement[:80])

        # Chroma 合并（简单覆盖）
        chroma_src = extract_dir / "chroma_db"
        if chroma_src.exists():
            chroma_dst = Path(settings.CHROMA_PERSIST_PATH)
            if chroma_dst.exists():
                shutil.rmtree(chroma_dst)
            shutil.copytree(chroma_src, chroma_dst)

        # SQLite 合并
        fb_src = extract_dir / "feedbacks.db"
        if fb_src.exists():
            conn = get_connection()
            src_conn = __import__("sqlite3").connect(str(fb_src))
            for table in ["feedbacks", "sync_log"]:
                try:
                    rows = src_conn.execute(f"SELECT * FROM {table}").fetchall()
                    cols = [d[0] for d in src_conn.execute(f"PRAGMA table_info({table})").fetchall()]
                    placeholders = ",".join(["?"] * len(cols))
                    for row in rows:
                        try:
                            conn.execute(
                                f"INSERT OR IGNORE INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
                                list(row),
                            )
                        except Exception:
                            logger.exception("SQLite row insert failed for table '%s'", table)
                except Exception:
                    logger.exception("SQLite table import failed for table '%s'", table)
            src_conn.close()
            conn.commit()
            conn.close()

        # 记录同步日志
        conn = get_connection()
        conn.execute(
            "INSERT INTO sync_log (direction, file_path, stats) VALUES (?, ?, ?)",
            ["import", zip_path, json.dumps({"cypher_imported": cypher_imported}, ensure_ascii=False)],
        )
        conn.commit()
        conn.close()

        return {"status": "ok", "sync_info": sync_info, "cypher_imported": cypher_imported}

    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)
