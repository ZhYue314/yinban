import re
from datetime import datetime
from typing import Any

from src.storage.database import get_db


class MemoryManager:
    async def get_recent_history(self, limit: int = 20) -> list[dict[str, Any]]:
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT role, message FROM chat_history ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [{"role": r["role"], "message": r["message"]} for r in reversed(rows)]
        finally:
            await db.close()

    async def get_relevant_memories(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT key, value, confidence FROM memories ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [{"key": r["key"], "value": r["value"], "confidence": r["confidence"]} for r in rows]
        finally:
            await db.close()

    async def store_memory(self, key: str, value: str, confidence: float = 1.0):
        db = await get_db()
        try:
            await db.execute(
                """INSERT INTO memories (key, value, confidence, updated_at)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value,
                       confidence=excluded.confidence, updated_at=excluded.updated_at""",
                (key, value, confidence, datetime.now().isoformat()),
            )
            await db.commit()
        finally:
            await db.close()

    async def extract_and_store(self, user_message: str, ai_reply: str):
        patterns = [
            (r"喜欢.*?(摇滚|流行|民谣|电子|嘻哈|爵士|古典|金属|R&B|雷鬼|轻音乐|后摇|独立|古风|说唱)", "likes_genre"),
            (r"(?:不喜欢|讨厌).*?(摇滚|流行|民谣|电子|嘻哈|爵士|古典|金属|R&B|雷鬼|轻音乐|后摇|独立|古风|说唱)", "dislikes_genre"),
            (r"(?:喜欢|爱听|推荐).*?歌手[：:\s]*(.+)", "likes_artist"),
            (r"(?:不喜欢|讨厌).*?歌手[：:\s]*(.+)", "dislikes_artist"),
            (r"最爱.*?《(.+?)》", "favorite_song"),
            (r"(?:推荐|分享).*?《(.+?)》", "shared_song"),
        ]

        for pattern, key in patterns:
            match = re.search(pattern, user_message)
            if match:
                await self.store_memory(key, match.group(1).strip(), 0.8)
