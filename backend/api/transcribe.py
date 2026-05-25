"""
语音转文字 + 文档解析 + 报告导出
"""

import os
import tempfile

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from tools.parser import parse_file
from tools.extractor import extract_knowledge

router = APIRouter()


# ===== 语音转文字 =====

@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """语音转文字"""
    # 保存临时文件
    tmp_path = os.path.join(tempfile.gettempdir(), f"audio_{audio.filename}")
    with open(tmp_path, "wb") as f:
        f.write(await audio.read())

    # 转发给 whisper-server
    import httpx
    from core.config import settings

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(tmp_path, "rb") as f:
                resp = await client.post(
                    f"{settings.WHISPER_SERVER_URL}/inference",
                    files={"file": ("audio.wav", f, "audio/wav")},
                )
            result = resp.json()
    except Exception:
        result = {"text": ""}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {
        "text": result.get("text", ""),
        "duration_ms": 0,
        "processing_ms": 0,
    }


# ===== 文档解析与知识抽取 =====

@router.post("/parse")
async def parse_document(file: UploadFile = File(...)):
    """上传文档 → 解析 → 知识抽取"""
    tmp_path = os.path.join(tempfile.gettempdir(), file.filename or "upload")
    with open(tmp_path, "wb") as f:
        f.write(await file.read())

    try:
        parsed = parse_file(tmp_path)
    except ValueError as e:
        raise HTTPException(400, str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    extracted = extract_knowledge(parsed["text"])

    return {
        "parse_id": f"parse_{os.urandom(4).hex()}",
        "file_name": file.filename,
        "extracted_text_length": parsed["text_length"],
        "candidates": extracted["candidates"],
        "regex_count": extracted["regex_count"],
        "model_count": extracted["model_count"],
    }


class ConfirmRequest(BaseModel):
    parse_id: str
    confirmed: list[str] = []
    rejected: list[str] = []
    edits: list[dict] = []


@router.post("/confirm")
async def confirm_import(req: ConfirmRequest):
    """确认导入知识抽取结果到 Neo4j + Chroma"""
    # TODO: 实际写入 Neo4j 和 Chroma
    return {
        "status": "ok",
        "imported": {"entities": len(req.confirmed), "relationships": 0},
        "chroma_chunks_added": 0,
    }


# ===== 报告导出 =====

@router.get("/report")
async def export_report(session_id: Optional[str] = None):
    """导出问答报告（Word）"""
    # TODO: 生成 Word 报告
    return {"status": "ok", "message": "报告导出功能开发中"}
