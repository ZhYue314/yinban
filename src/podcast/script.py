from typing import Any

from src.ai.llm import LLMClient
from src.ai.prompts import DAILY_REPORT_PROMPT
from src.core.personality import Personality


class ScriptGenerator:
    def __init__(self, personality: Personality, llm: LLMClient):
        self.personality = personality
        self.llm = llm

    async def generate_daily_script(self, songs: list[dict[str, Any]]) -> str:
        prompt = DAILY_REPORT_PROMPT.format(
            mood=self.personality.today_mood,
            energy=self.personality.energy,
            count=len(songs),
        )
        messages = [
            {"role": "system", "content": self.personality.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        return await self.llm.chat(messages)

    async def generate_recommend_script(
        self, songs: list[dict[str, Any]], reason: str
    ) -> str:
        return reason
