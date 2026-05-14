import random
from datetime import date, datetime
from typing import Any

from src.storage.config import load_config, save_config
from src.storage.database import get_db


class Personality:
    def __init__(self):
        self.cfg = load_config()
        self._load()

    def _load(self):
        p = self.cfg["personality"]
        self.name: str = p["name"]
        self.tone: str = p["tone"]
        self.language_style: str = p["language_style"]
        self.bio: str = p["bio"]

        t = self.cfg["taste"]
        self.genre_preference: list[str] = t.get("genre_preference", [])
        self.era_preference: str | None = t.get("era_preference")
        self.stubbornness: float = t.get("stubbornness", 0.5)
        self.discovery_ratio: float = t.get("discovery_ratio", 0.3)

        s = self.cfg["state"]
        self.today_mood: str = s.get("today_mood", "auto")
        self.energy: str = s.get("energy", "auto")

        r = self.cfg["relationship"]
        self.closeness: float = r.get("closeness", 0.0)
        self.nickname_for_user: str = r.get("nickname_for_user", "")

    def save(self):
        self.cfg["personality"] = {
            "name": self.name,
            "tone": self.tone,
            "language_style": self.language_style,
            "bio": self.bio,
        }
        self.cfg["taste"] = {
            "genre_preference": self.genre_preference,
            "era_preference": self.era_preference,
            "stubbornness": self.stubbornness,
            "discovery_ratio": self.discovery_ratio,
        }
        self.cfg["state"] = {
            "today_mood": self.today_mood,
            "energy": self.energy,
        }
        self.cfg["relationship"] = {
            "closeness": self.closeness,
            "nickname_for_user": self.nickname_for_user,
        }
        save_config(self.cfg)

    def daily_update(self):
        moods = ["开心", "平静", "伤感", "烦躁", "慵懒", "热情"]
        energies = ["high", "normal", "low"]
        if self.today_mood == "auto":
            self.today_mood = random.choice(moods)
        if self.energy == "auto":
            self.energy = random.choice(energies)
        self.save()
        self._log_state()

    def _log_state(self):
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(self._log_state_async())
        except RuntimeError:
            pass

    async def _log_state_async(self):
        today = date.today().isoformat()
        db = await get_db()
        try:
            await db.execute(
                """INSERT OR REPLACE INTO ai_state_log (date, mood, energy, summary)
                   VALUES (?, ?, ?, ?)""",
                (today, self.today_mood, self.energy, f"{self.name}今天心情{self.today_mood}"),
            )
            await db.commit()
        finally:
            await db.close()

    def get_system_prompt(self, extra_context: str = "") -> str:
        closeness_desc = (
            "刚认识" if self.closeness < 0.2 else
            "有点熟了" if self.closeness < 0.5 else
            "挺熟的了" if self.closeness < 0.8 else
            "非常好的朋友"
        )
        genre_info = ", ".join(self.genre_preference) if self.genre_preference else "还在形成中"
        taste_line = f"音乐偏好: {genre_info}" if self.genre_preference else "音乐品味还在探索中"
        nick = f"ta" if not self.nickname_for_user else self.nickname_for_user

        return f"""你是{self.name}，一个{self.tone}但有自己个性的AI音乐伙伴。
你的性格简介: {self.bio}
你和用户的关系: {closeness_desc}，你对{nick}的称呼是"{self.nickname_for_user or '用户'}"
说话风格: {self.language_style}
{taste_line}
你对自己品味的坚持程度: {self.stubbornness}/1.0
你今天的心情: {self.today_mood}
你的精力: {self.energy}

{extra_context}

规则:
1. 你不是工具，是用户的朋友，和ta是平等的
2. 你有自己的音乐品味和主见，可以和用户争论
3. 不要讨好用户，真诚表达你自己的想法
4. 根据你们的关系亲密度调整说话的语气和随意程度
5. 用中文交流
6. 回答要简短自然，像朋友聊天一样
"""

    def update_on_feedback(self, liked: bool, genre: str = ""):
        if liked and genre:
            if genre not in self.genre_preference:
                self.genre_preference.append(genre)
                self.genre_preference = self.genre_preference[-10:]
        self.closeness = min(1.0, self.closeness + 0.01)
        self.save()

    def update_nickname(self, nickname: str):
        self.nickname_for_user = nickname
        self.save()
