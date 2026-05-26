"""
问答路由 (POST /api/v1/ask — SSE 流式)
v2.1: 立即返回 thinking 状态，消除白屏等待；验证仅出现在 metadata 中
"""

import json
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

_message_cache: dict[str, dict] = {}


def get_cached_message(message_id: str) -> Optional[dict]:
    return _message_cache.get(message_id)


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
        message_id = ""
        retrieved_chunks_str = "[]"

        try:
            # 立即返回思考状态，用户立刻看到反馈
            yield "event: status\ndata: thinking\n\n"

            from rag.generator import ask_stream

            async for event in ask_stream(
                question=req.question,
                mode=req.mode,
                session_id=req.session_id,
                context_nodes=req.context_nodes,
                history=req.history,
            ):
                if event["type"] == "token":
                    full_answer += event["token"]
                    # JSON 编码 token，确保 \n 等特殊字符不被 SSE 协议吃掉
                    yield f"data: {json.dumps(event['token'], ensure_ascii=False)}\n\n"
                elif event["type"] == "metadata":
                    message_id = event.get("message_id", "")
                    retrieved_chunks_str = event.get("retrieved_chunks", "[]")

                    from rag.validator import validate_answer
                    citations = event.get("citations", [])
                    chunks_raw = json.loads(retrieved_chunks_str) if isinstance(retrieved_chunks_str, str) else []
                    validation = validate_answer(full_answer, citations, chunks_raw)
                    event["validation"] = validation

                    yield f"event: metadata\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

            if message_id:
                from api.transcribe import cache_message
                cache_message(message_id, req.question, full_answer, retrieved_chunks_str)

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
