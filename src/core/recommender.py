import random
from datetime import datetime
from typing import Any

from src.core.personality import Personality
from src.storage.database import get_db


class Recommender:
    def __init__(self, personality: Personality):
        self.personality = personality

    async def recommend_from_liked(self, limit: int = 5) -> list[dict[str, Any]]:
        db = await get_db()

        cursor = await db.execute(
            "SELECT artist, genre FROM liked_songs ORDER BY synced_at DESC LIMIT 50"
        )
        liked = await cursor.fetchall()
        liked_count = len(liked)

        if liked_count == 0:
            await db.close()
            return []

        top_artists = []
        cursor = await db.execute(
            "SELECT artist_name, listen_count FROM user_artists ORDER BY listen_count DESC LIMIT 5"
        )
        for row in await cursor.fetchall():
            top_artists.append(row["artist_name"])

        recommendations = []
        cursor = await db.execute(
            "SELECT DISTINCT artist FROM all_songs WHERE artist != '' ORDER BY RANDOM() LIMIT ?",
            (limit * 3,),
        )
        candidates = await cursor.fetchall()

        for row in candidates:
            if row["artist"] and len(recommendations) < limit:
                recommendations.append({
                    "name": row["artist"],
                    "artist": "",
                    "reason": "风格相似，你可能也会喜欢",
                })

        if len(recommendations) < limit:
            cursor = await db.execute(
                "SELECT name, artist FROM all_songs WHERE artist IN ("
                + ",".join("?" for _ in top_artists[:3])
                + ") ORDER BY RANDOM() LIMIT ?",
                [*top_artists[:3], limit - len(recommendations)],
            )
            for row in await cursor.fetchall():
                recommendations.append({
                    "name": row["name"],
                    "artist": row["artist"],
                    "reason": f"来自你常听的 {row['artist']}",
                })

        await db.close()
        return recommendations[:limit]

    async def recommend_by_mood(self, mood: str, limit: int = 5) -> list[dict[str, Any]]:
        db = await get_db()
        cursor = await db.execute(
            "SELECT name, artist FROM all_songs ORDER BY RANDOM() LIMIT ?",
            (limit,),
        )
        songs = await cursor.fetchall()
        await db.close()

        mood_descriptions = {
            "开心": "轻快活泼",
            "平静": "舒缓放松",
            "伤感": "温柔治愈",
            "烦躁": "安静舒缓",
            "慵懒": "松弛惬意",
            "热情": "充满活力",
        }
        desc = mood_descriptions.get(mood, "")

        return [
            {"name": s["name"], "artist": s["artist"], "reason": f"适合{mood}的时候听，{desc}"}
            for s in songs
        ]

    async def recommend_by_scene(self, scene: str, limit: int = 5) -> list[dict[str, Any]]:
        db = await get_db()
        cursor = await db.execute(
            "SELECT name, artist FROM all_songs ORDER BY RANDOM() LIMIT ?",
            (limit,),
        )
        songs = await cursor.fetchall()
        await db.close()

        scene_desc = {
            "深夜": "安静陪着你",
            "学习": "帮助专注",
            "跑步": "节奏感强",
            "通勤": "路上不无聊",
            "工作": "提升效率",
        }
        desc = scene_desc.get(scene, "适合这个场景")

        return [
            {"name": s["name"], "artist": s["artist"], "reason": desc}
            for s in songs
        ]

    async def get_daily_recommendation(self) -> dict[str, Any]:
        self.personality.daily_update()
        songs = await self.recommend_from_liked(5)
        return {
            "mood": self.personality.today_mood,
            "energy": self.personality.energy,
            "songs": songs,
        }

    async def discover_artists(self, limit: int = 5) -> dict[str, Any]:
        db = await get_db()
        cursor = await db.execute(
            "SELECT artist_name, listen_count FROM user_artists ORDER BY listen_count DESC LIMIT 10"
        )
        top = await cursor.fetchall()
        await db.close()

        return {
            "top_artists": [{"name": a["artist_name"], "count": a["listen_count"]} for a in top],
        }
