"""
SQLite 数据库初始化和基础操作

表: users, feedbacks, conversations, messages, sync_log
"""

import sqlite3
from pathlib import Path

from core.config import settings

DB_PATH = Path(settings.SQLITE_PATH)


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """创建所有表（幂等）"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            display_name  TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin')),
            avatar_color  TEXT DEFAULT '#1890ff',
            created_at    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS conversations (
            session_id   TEXT PRIMARY KEY,
            user_id      INTEGER REFERENCES users(id),
            title        TEXT NOT NULL,
            message_count INTEGER NOT NULL DEFAULT 0,
            pinned       INTEGER NOT NULL DEFAULT 0,
            created_at   TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_conversations_user
            ON conversations(user_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_pinned
            ON conversations(pinned);

        CREATE TABLE IF NOT EXISTS messages (
            message_id   TEXT PRIMARY KEY,
            session_id   TEXT NOT NULL REFERENCES conversations(session_id) ON DELETE CASCADE,
            role         TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content      TEXT NOT NULL,
            citations    TEXT,
            traceability TEXT,
            created_at   TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session
            ON messages(session_id);

        CREATE TABLE IF NOT EXISTS feedbacks (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id       TEXT NOT NULL UNIQUE,
            user_id          INTEGER REFERENCES users(id),
            question         TEXT NOT NULL,
            answer_text      TEXT NOT NULL,
            rating           INTEGER NOT NULL CHECK(rating IN (-1, 0, 1)),
            comment          TEXT,
            retrieved_chunks TEXT NOT NULL,
            traceability     TEXT,
            created_at       TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_feedbacks_rating
            ON feedbacks(rating);
        CREATE INDEX IF NOT EXISTS idx_feedbacks_user
            ON feedbacks(user_id);

        CREATE TABLE IF NOT EXISTS sync_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            direction   TEXT NOT NULL CHECK(direction IN ('export', 'import')),
            file_path   TEXT,
            stats       TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()
