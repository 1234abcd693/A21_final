"""
用户认证 + 用户管理 + 个人统计
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from data.database import get_connection

router = APIRouter()
_sessions: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "user"


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    password: Optional[str] = None
    avatar_color: Optional[str] = None


def _hash_password(password: str) -> str:
    """bcrypt 密码哈希（自动降级到 hashlib）"""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    except ImportError:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ImportError, ValueError):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == password_hash


def _create_admin_if_not_exists():
    conn = get_connection()
    user = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
    if not user:
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)",
            ["admin", _hash_password("admin123"), "管理员", "admin"],
        )
        conn.commit()
    conn.close()


_create_admin_if_not_exists()


# ===== 认证 =====

@router.post("/auth/register")
async def register(req: RegisterRequest):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)",
            [req.username, _hash_password(req.password), req.display_name, req.role],
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return {"status": "ok", "user_id": user_id}
    except Exception as e:
        raise HTTPException(400, f"注册失败: {str(e)}")
    finally:
        conn.close()


@router.post("/auth/login")
async def login(req: LoginRequest):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", [req.username]).fetchone()
    conn.close()
    if not user or not _verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "用户名或密码错误")
    token = uuid.uuid4().hex
    _sessions[token] = dict(user)
    return {
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "display_name": user["display_name"], "role": user["role"]},
    }


@router.get("/auth/me")
async def me(token: str = ""):
    user = _sessions.get(token)
    if not user:
        raise HTTPException(401, "未登录")
    return {"id": user["id"], "username": user["username"], "display_name": user["display_name"], "role": user["role"]}


# ===== 用户管理 =====

@router.get("/users")
async def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, display_name, role, created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return {"users": [dict(r) for r in rows]}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM conversations WHERE user_id = ?", [user_id])
    conn.execute("DELETE FROM feedbacks WHERE user_id = ?", [user_id])
    conn.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", [user_id])
    conn.commit()
    conn.close()
    return {"status": "ok"}


# ===== 个人中心 =====

@router.get("/user/stats")
async def user_stats(token: str = ""):
    """个人统计"""
    user = _sessions.get(token)
    if not user:
        raise HTTPException(401, "未登录")
    conn = get_connection()
    uid = user["id"]
    q_count = conn.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", [uid]).fetchone()[0]
    likes = conn.execute("SELECT COUNT(*) FROM feedbacks WHERE user_id = ? AND rating = 1", [uid]).fetchone()[0]
    dislikes = conn.execute("SELECT COUNT(*) FROM feedbacks WHERE user_id = ? AND rating = -1", [uid]).fetchone()[0]
    conn.close()
    return {"stats": {"total_questions": q_count, "total_likes": likes, "total_dislikes": dislikes, "active_days": 1}}


@router.put("/user/profile")
async def update_profile(req: ProfileUpdate, token: str = ""):
    """修改个人设置"""
    user = _sessions.get(token)
    if not user:
        raise HTTPException(401, "未登录")
    conn = get_connection()
    if req.display_name:
        conn.execute("UPDATE users SET display_name = ? WHERE id = ?", [req.display_name, user["id"]])
    if req.password:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", [_hash_password(req.password), user["id"]])
    if req.avatar_color:
        conn.execute("UPDATE users SET avatar_color = ? WHERE id = ?", [req.avatar_color, user["id"]])
    conn.commit()
    conn.close()
    return {"status": "ok"}
