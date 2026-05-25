"""
用户认证 + 用户管理路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# 简化的内存 token（本地应用不需要 JWT）
_sessions: dict[str, dict] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "user"


def _hash_password(password: str) -> str:
    """密码哈希（生产环境用 bcrypt，开发阶段用简单哈希）"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, password_hash: str) -> bool:
    return _hash_password(password) == password_hash


def _create_admin_if_not_exists():
    """首次启动时自动创建 admin 账号"""
    from data.database import get_connection
    conn = get_connection()
    user = conn.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1").fetchone()
    if not user:
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)",
            ["admin", _hash_password("admin123"), "管理员", "admin"],
        )
        conn.commit()
    conn.close()


# 模块加载时创建 admin
_create_admin_if_not_exists()


@router.post("/auth/register")
async def register(req: RegisterRequest):
    """管理员注册新用户"""
    from data.database import get_connection
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)",
            [req.username, _hash_password(req.password), req.display_name, req.role],
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return {"status": "ok", "user_id": user_id}
    except Exception as e:
        raise HTTPException(400, f"注册失败: {str(e)}")


@router.post("/auth/login")
async def login(req: LoginRequest):
    """登录"""
    from data.database import get_connection
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?", [req.username]
    ).fetchone()
    conn.close()

    if not user or not _verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "用户名或密码错误")

    import uuid
    token = uuid.uuid4().hex
    _sessions[token] = dict(user)

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "display_name": user["display_name"],
            "role": user["role"],
        },
    }


@router.get("/auth/me")
async def me(token: str = ""):
    """当前登录用户（传入 login 返回的 token）"""
    user = _sessions.get(token)
    if not user:
        raise HTTPException(401, "未登录")
    return {
        "id": user["id"],
        "username": user["username"],
        "display_name": user["display_name"],
        "role": user["role"],
    }


@router.get("/users")
async def list_users():
    """用户列表（admin）"""
    from data.database import get_connection
    conn = get_connection()
    rows = conn.execute("SELECT id, username, display_name, role, created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return {"users": [dict(r) for r in rows]}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """删除用户"""
    from data.database import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM conversations WHERE user_id = ?", [user_id])
    conn.execute("DELETE FROM feedbacks WHERE user_id = ?", [user_id])
    conn.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", [user_id])
    conn.commit()
    conn.close()
    return {"status": "ok"}
