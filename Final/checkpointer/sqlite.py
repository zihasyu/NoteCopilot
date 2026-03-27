"""
SQLite Checkpointer - 对话状态持久化
支持长程多轮交互中的上下文记忆
"""
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, Optional

from langgraph.checkpoint.sqlite import SqliteSaver


class ConversationMemory:
    """对话记忆管理器"""

    def __init__(self, db_path: str = "./checkpoints/conversations.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """确保数据库和表存在"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                thread_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # 状态检查点表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT,
                checkpoint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES conversations(thread_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_thread(self, thread_id: str, metadata: dict = None) -> bool:
        """创建新会话线程"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO conversations (thread_id, metadata) VALUES (?, ?)",
                (thread_id, json.dumps(metadata) if metadata else None)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_thread(self, thread_id: str) -> Optional[dict]:
        """获取会话信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM conversations WHERE thread_id = ?",
            (thread_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "thread_id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "metadata": json.loads(row[3]) if row[3] else {}
            }
        return None

    def save_checkpoint(self, thread_id: str, state: dict):
        """保存状态检查点"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO checkpoints (thread_id, checkpoint) VALUES (?, ?)",
            (thread_id, json.dumps(state, ensure_ascii=False))
        )

        cursor.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
            (thread_id,)
        )

        conn.commit()
        conn.close()

    def get_latest_checkpoint(self, thread_id: str) -> Optional[dict]:
        """获取最新检查点"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """SELECT checkpoint FROM checkpoints
               WHERE thread_id = ?
               ORDER BY created_at DESC LIMIT 1""",
            (thread_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def list_threads(self) -> list:
        """列出所有会话线程"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT thread_id, updated_at FROM conversations ORDER BY updated_at DESC"
        )

        rows = cursor.fetchall()
        conn.close()

        return [{"thread_id": r[0], "updated_at": r[1]} for r in rows]


def create_checkpointer(db_path: str = "./checkpoints/langgraph.db"):
    """
    创建 LangGraph 兼容的 SqliteSaver

    Args:
        db_path: SQLite 数据库路径

    Returns:
        SqliteSaver 实例
    """
    import os
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    return SqliteSaver.from_conn_string(db_path)
