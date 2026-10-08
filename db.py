from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from config import BASE_DIR, settings

DB_PATH = Path(settings.db_path).resolve() if settings.db_path else BASE_DIR / "data" / "bot.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                document_name TEXT,
                question_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'success'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def ensure_user(user_id: int, full_name: str | None, username: str | None) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, full_name, username)
            VALUES (?, ?, ?)
            """,
            (user_id, full_name, username),
        )
        conn.commit()
    finally:
        conn.close()


def get_today_usage_count(user_id: int) -> int:
    today = date.today().isoformat()
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM document_usage
            WHERE user_id = ? AND date(created_at) = ?
            """,
            (user_id, today),
        ).fetchone()
        return int(row["total"]) if row else 0
    finally:
        conn.close()


def record_document_usage(user_id: int, document_name: str, question_count: int, status: str = "success") -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO document_usage (user_id, document_name, question_count, status)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, document_name, question_count, status),
        )
        conn.commit()
    finally:
        conn.close()
