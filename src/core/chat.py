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

    async def chat(self, user_message: str) -> str:
        history = await self.memory.get_recent_history(10)
        memories = await self.memory.get_relevant_memories(user_message, limit=5)
        system_prompt = self.personality.get_system_prompt()

        memory_summary = "\n".join(
            f"- {m['key']}: {m['value']}" for m in memories
        ) if memories else "暂无"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"关于用户的记忆:\n{memory_summary}"},
        ]

        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["message"]})

        messages.append({"role": "user", "content": user_message})

        reply = await self.llm.chat(messages)

        db = await get_db()
        now = datetime.now().isoformat()
        await db.execute(
            "INSERT INTO chat_history (role, message, created_at) VALUES (?, ?, ?)",
            ("user", user_message, now),
        )
        await db.execute(
            "INSERT INTO chat_history (role, message, created_at) VALUES (?, ?, ?)",
            ("ai", reply, now),
        )
        await db.commit()
        await db.close()

        await self.memory.extract_and_store(user_message, reply)

        self.personality.closeness = min(1.0, self.personality.closeness + 0.005)
        self.personality.save()

        return reply
