"""
反馈数据存储（SQLite）
"""

import json
from typing import Any, Optional

from data.database import get_connection


def save_feedback(
    message_id: str,
    question: str,
    answer_text: str,
    rating: int,
    retrieved_chunks: str,
    traceability: Optional[str] = None,
    user_id: Optional[int] = None,
    comment: Optional[str] = None,
) -> None:
    """保存一条反馈（INSERT OR REPLACE 幂等）"""
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO feedbacks
            (message_id, user_id, question, answer_text, rating, comment, retrieved_chunks, traceability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [message_id, user_id, question, answer_text, rating, comment, retrieved_chunks, traceability])
    conn.commit()
    conn.close()


def get_feedbacks(limit: int = 100, rating_filter: Optional[int] = None) -> list[dict[str, Any]]:
    """获取反馈列表（优化器使用）"""
    conn = get_connection()
    query = "SELECT * FROM feedbacks"
    params: list = []
    if rating_filter is not None:
        query += " WHERE rating = ?"
        params.append(rating_filter)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for row in rows:
        d = dict(row)
        d["retrieved_chunks"] = json.loads(d["retrieved_chunks"]) if d["retrieved_chunks"] else []
        results.append(d)
    return results


def get_feedback_count() -> int:
    """获取反馈总数"""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM feedbacks").fetchone()[0]
    conn.close()
    return count
