from typing import Any

from src.ai.llm import LLMClient
from src.ai.prompts import PODCAST_DAILY_PROMPT
from src.core.personality import Personality


class ScriptGenerator:
    def __init__(self, personality: Personality, llm: LLMClient):
        self.personality = personality
        self.llm = llm

    async def generate_daily_script(self, songs: list[dict[str, Any]]) -> str:
        if not songs:
            return f"大家好，我是{self.personality.name}。今天好像没什么新歌推荐，可能你最近听歌少了？有空来跟我聊聊吧。"

        song_lines = "\n".join(
            f"- 《{s.get('name', '未知')}》{s.get('artist', '')}" for s in songs
        )
        prompt = PODCAST_DAILY_PROMPT.format(
            name=self.personality.name,
            mood=self.personality.today_mood,
            energy=self.personality.energy,
            count=len(songs),
            songs=song_lines,
        )
        messages = [
            {"role": "system", "content": self.personality.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        return await self.llm.chat(messages)

    async def generate_recommend_script(
        self, songs: list[dict[str, Any]], mood: str = ""
    ) -> str:
        if not songs:
            return "今天没什么想推荐的，可能我心情不太好。改天吧。"

        song_lines = "\n".join(
            f"- 《{s.get('name', '未知')}》{s.get('artist', '')} - {s.get('reason', '')}"
            for s in songs
        )
        mood_line = f"我知道你现在心情{mood}，" if mood else ""
        prompt = f"""{mood_line}给我推荐{len(songs)}首歌。
用你{self.personality.tone}的语气，像朋友聊天一样说出来。

{song_lines}

把上面的内容组织成一段自然的播报，不要列清单，要连贯地说出来。"""
        messages = [
            {"role": "system", "content": self.personality.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        return await self.llm.chat(messages)
