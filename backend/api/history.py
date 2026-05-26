"""
历史对话管理路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from data.database import get_connection

router = APIRouter()


@router.get("/history")
async def list_history(
    user_id: int = 0,
    page: int = 1,
    page_size: int = 20,
):
    """历史对话列表"""
    offset = (page - 1) * page_size
    conn = get_connection()

    count_row = conn.execute(
        "SELECT COUNT(*) FROM conversations WHERE (? = 0 OR user_id = ?)",
        [user_id, user_id],
    ).fetchone()
    total = count_row[0] if count_row else 0

    rows = conn.execute("""
        SELECT * FROM conversations
        WHERE (? = 0 OR user_id = ?)
        ORDER BY pinned DESC, updated_at DESC
        LIMIT ? OFFSET ?
    """, [user_id, user_id, page_size, offset]).fetchall()
    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "sessions": [dict(r) for r in rows],
    }


@router.get("/history/search")
async def search_history(
    q: str = "",
    page: int = 1,
    page_size: int = 20,
):
    """搜索历史对话"""
    offset = (page - 1) * page_size
    conn = get_connection()
    keyword = f"%{q}%"
    rows = conn.execute("""
        SELECT c.* FROM conversations c
        WHERE c.title LIKE ? OR c.session_id IN (
            SELECT DISTINCT m.session_id FROM messages m WHERE m.content LIKE ?
        )
        ORDER BY c.pinned DESC, c.updated_at DESC
        LIMIT ? OFFSET ?
    """, [keyword, keyword, page_size, offset]).fetchall()
    conn.close()

    return {
        "query": q,
        "total": len(rows),
        "sessions": [dict(r) for r in rows],
    }


@router.get("/history/{session_id}")
async def get_history_detail(session_id: str):
    """获取对话详情"""
    conn = get_connection()
    session_row = conn.execute(
        "SELECT * FROM conversations WHERE session_id = ?", [session_id]
    ).fetchone()
    if not session_row:
        conn.close()
        raise HTTPException(404, "会话不存在")

    messages = conn.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at",
        [session_id],
    ).fetchall()
    conn.close()

    return {
        "session_id": session_id,
        "title": session_row["title"],
        "messages": [dict(r) for r in messages],
    }


@router.delete("/history/{session_id}")
async def delete_history(session_id: str):
    """删除单个会话"""
    conn = get_connection()
    conn.execute("DELETE FROM messages WHERE session_id = ?", [session_id])
    conn.execute("DELETE FROM conversations WHERE session_id = ?", [session_id])
    conn.commit()
    conn.close()
    return {"status": "ok", "deleted_session": session_id}


@router.patch("/history/{session_id}")
async def pin_history(session_id: str, pinned: bool = True):
    """置顶/取消置顶"""
    conn = get_connection()
    conn.execute(
        "UPDATE conversations SET pinned = ? WHERE session_id = ?",
        [1 if pinned else 0, session_id],
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "session_id": session_id, "pinned": pinned}


class BatchDeleteRequest(BaseModel):
    session_ids: list[str]


class SaveHistoryRequest(BaseModel):
    session_id: str
    title: str = ""
    user_msg: str = ""
    assistant_msg: str = ""
    user_id: int = 0


@router.post("/history/save")
async def save_history(req: SaveHistoryRequest):
    conn = get_connection()
    uid = req.session_id
    conn.execute("INSERT OR REPLACE INTO conversations (session_id, user_id, title, message_count, updated_at) VALUES (?,?,?,2,datetime('now'))", [uid, req.user_id if req.user_id else None, req.title])
    conn.execute("INSERT OR REPLACE INTO messages (message_id, session_id, role, content) VALUES (?,?,?,?)", [uid + "_u", uid, "user", req.user_msg])
    conn.execute("INSERT OR REPLACE INTO messages (message_id, session_id, role, content) VALUES (?,?,?,?)", [uid + "_a", uid, "assistant", req.assistant_msg])
    conn.commit()
    conn.close()
    return {"status": "ok"}


@router.put("/history/{session_id}/rename")
async def rename_history(session_id: str, title: str = ""):
    """重命名会话"""
    if not title.strip():
        raise HTTPException(400, "标题不能为空")
    conn = get_connection()
    conn.execute(
        "UPDATE conversations SET title = ?, updated_at = datetime('now') WHERE session_id = ?",
        [title.strip(), session_id],
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "session_id": session_id, "title": title.strip()}


@router.delete("/history/batch")
async def batch_delete_history(req: BatchDeleteRequest):
    """批量删除会话"""
    conn = get_connection()
    for sid in req.session_ids:
        conn.execute("DELETE FROM messages WHERE session_id = ?", [sid])
        conn.execute("DELETE FROM conversations WHERE session_id = ?", [sid])
    conn.commit()
    conn.close()
    return {"status": "ok", "deleted_count": len(req.session_ids)}
