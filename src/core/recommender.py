import random
from typing import Any

from src.core.personality import Personality
from src.storage.database import get_db


class Recommender:
    def __init__(self, personality: Personality):
        self.personality = personality

    async def recommend_from_liked(self, limit: int = 5) -> list[dict[str, Any]]:
        db = await get_db()
        cursor = await db.execute(
            "SELECT artist, genre FROM liked_songs ORDER BY synced_at DESC LIMIT 20"
        )
        liked = await cursor.fetchall()
        await db.close()

        artists = set(row["artist"] for row in liked if row["artist"])
        genres = set(row["genre"] for row in liked if row["genre"])

        return {
            "artists": list(artists),
            "genres": list(genres),
            "count": len(liked),
        }

    async def recommend_by_mood(self, mood: str, limit: int = 5) -> list[dict[str, Any]]:
        return {"mood": mood, "message": f"根据心情{mood}推荐歌曲"}

    async def recommend_by_scene(self, scene: str, limit: int = 5) -> list[dict[str, Any]]:
        return {"scene": scene, "message": f"根据场景{scene}推荐歌曲"}

    async def get_daily_recommendation(self) -> dict[str, Any]:
        self.personality.daily_update()
        return {
            "mood": self.personality.today_mood,
            "energy": self.personality.energy,
            "message": "每日推荐已生成",
        }

    async def discover_artists(self, limit: int = 5) -> list[dict[str, Any]]:
        return {"message": "发现新歌手功能待实现"}
