from datetime import datetime
from typing import Any

from src.ai.memory import MemoryManager
from src.ai.llm import LLMClient
from src.core.personality import Personality
from src.storage.database import get_db


class ChatEngine:
    def __init__(self, personality: Personality, llm: LLMClient):
        self.personality = personality
        self.llm = llm
        self.memory = MemoryManager()

    async def _get_music_context(self) -> str:
        db = await get_db()
        parts = []
        try:
            c = await db.execute("SELECT COUNT(*) as c FROM liked_songs")
            liked_count = (await c.fetchone())["c"]
            if liked_count:
                parts.append(f"用户收藏了 {liked_count} 首歌曲")

            c = await db.execute("SELECT artist_name, listen_count FROM user_artists ORDER BY listen_count DESC LIMIT 3")
            artists = await c.fetchall()
            if artists:
                names = [a["artist_name"] for a in artists]
                parts.append(f"常听的歌手: {', '.join(names)}")

            c = await db.execute("SELECT name, artist FROM all_songs ORDER BY RANDOM() LIMIT 3")
            some = await c.fetchall()
            if some:
                examples = [f"{s['name']} - {s['artist']}" for s in some]
                parts.append(f"曲库中包括: {', '.join(examples)}")
        finally:
            await db.close()
        return " | ".join(parts) if parts else ""

    async def chat(self, user_message: str) -> str:
        history = await self.memory.get_recent_history(10)
        memories = await self.memory.get_relevant_memories(user_message, limit=5)
        music_ctx = await self._get_music_context()
        system_prompt = self.personality.get_system_prompt(music_ctx)

        memory_summary = "\n".join(
            f"- {m['key']}: {m['value']}" for m in memories
        ) if memories else "暂无"

        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if memories:
            messages.append({"role": "system", "content": f"关于用户的记忆:\n{memory_summary}"})

        for h in history[-8:]:
            messages.append({"role": h["role"], "content": h["message"]})

        messages.append({"role": "user", "content": user_message})

        reply = await self.llm.chat(messages)

        db = await get_db()
        now = datetime.now().isoformat()
        try:
            await db.execute(
                "INSERT INTO chat_history (role, message, created_at) VALUES (?, ?, ?)",
                ("user", user_message, now),
            )
            await db.execute(
                "INSERT INTO chat_history (role, message, created_at) VALUES (?, ?, ?)",
                ("ai", reply, now),
            )
            await db.commit()
        finally:
            await db.close()

        await self.memory.extract_and_store(user_message, reply)

        self.personality.closeness = min(1.0, self.personality.closeness + 0.005)
        self.personality.save()

        return reply
