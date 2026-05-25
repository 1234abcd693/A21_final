"""
问答路由 (POST /api/v1/ask — SSE 流式)
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag.generator import ask_stream
from rag.validator import validate_answer, format_warning

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    mode: str = "chat"
    session_id: Optional[str] = None
    context_nodes: Optional[list[str]] = None
    history: Optional[list[dict]] = None


@router.post("/ask")
async def ask(req: AskRequest):
    """核心问答接口，SSE 流式返回"""

    async def event_generator():
        full_answer = ""
        citations = []

        try:
            async for event in ask_stream(
                question=req.question,
                mode=req.mode,
                session_id=req.session_id,
                context_nodes=req.context_nodes,
                history=req.history,
            ):
                if event["type"] == "token":
                    full_answer += event["token"]
                    yield f"data: {event['token']}\n\n"
                elif event["type"] == "metadata":
                    citations = event["citations"]
                    # 验证
                    retrieved_chunks_str = event.get("retrieved_chunks", "[]")
                    import json
                    chunks = json.loads(retrieved_chunks_str) if isinstance(retrieved_chunks_str, str) else []
                    validation = validate_answer(full_answer, citations, chunks)
                    warning = format_warning(validation["confidence"])

                    if warning:
                        full_answer += f"\n\n{warning}"
                        yield f"data: {warning}\n\n"

                    event["traceability"] = validation
                    yield f"event: metadata\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

            yield "event: done\ndata: {}\n\n"

        except Exception as e:
            yield f"data: [错误: {str(e)}]\n\n"
            yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
