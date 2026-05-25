"""
反馈与优化路由
"""

import json
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from feedback.storage import save_feedback, get_feedbacks, get_feedback_count
from feedback.optimizer.grid_search import GridSearchOptimizer
from feedback.config import apply_optimized, load, reset_to_defaults

router = APIRouter()


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int
    question: str = ""
    answer_text: str = ""
    retrieved_chunks: str = "[]"
    comment: Optional[str] = None


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    """提交点赞/点踩"""
    if req.rating not in (-1, 0, 1):
        raise HTTPException(400, "rating must be -1, 0, or 1")

    save_feedback(
        message_id=req.message_id,
        question=req.question,
        answer_text=req.answer_text,
        rating=req.rating,
        retrieved_chunks=req.retrieved_chunks or "[]",
        comment=req.comment,
    )
    return {"status": "ok", "total_feedbacks": get_feedback_count()}


@router.post("/optimize")
async def trigger_optimization():
    """手动触发参数优化"""
    feedbacks = get_feedbacks(limit=100, rating_filter=None)
    positive_feedbacks = [f for f in feedbacks if f.get("rating") != 0]

    if len(positive_feedbacks) < 5:
        return {"status": "insufficient_data", "feedbacks_available": len(positive_feedbacks)}

    optimizer = GridSearchOptimizer()
    best_params = optimizer.optimize(positive_feedbacks)

    previous_params = load().get("retrieval", {})
    apply_optimized(best_params)

    return {
        "status": "completed",
        "feedbacks_used": len(positive_feedbacks),
        "best_params": best_params,
        "previous_score": 0.0,
        "improvement": best_params.get("score", 0.0),
    }


@router.get("/params")
async def get_params():
    """获取当前 RAG 参数"""
    return load()


@router.post("/params/reset")
async def reset_params():
    """恢复默认参数"""
    params = reset_to_defaults()
    return {"status": "ok", "params": params["retrieval"]}
