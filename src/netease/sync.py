from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from src.storage.database import get_db


class NeteaseSync:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self, cookies: dict[str, str] | None = None):
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                cookies=cookies or {},
                timeout=30.0,
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        try:
            await self._ensure_client()
            resp = await self._client.get("/")
            return resp.status_code == 200
        except Exception:
            return False

    async def get_account_info(self, cookies: dict[str, str]) -> dict[str, Any]:
        await self._ensure_client(cookies)
        resp = await self._client.get("/user/account")
        return resp.json()

    async def get_user_info(self, uid: str, cookies: dict[str, str]) -> dict[str, Any]:
        await self._ensure_client(cookies)
        resp = await self._client.get("/user/detail", params={"uid": uid})
        return resp.json()

    async def sync_liked_songs(self, uid: str, cookies: dict[str, str]) -> int:
        await self._ensure_client(cookies)
        all_ids = set()
        offset = 0
        limit = 100

        while True:
            resp = await self._client.get("/likelist", params={"uid": uid})
            data = resp.json()
            ids = data.get("ids", [])
            if not ids:
                break
            all_ids.update(ids)
            if len(ids) < limit:
                break
            offset += limit

        song_ids = list(all_ids)
        synced = 0
        now = datetime.now().isoformat()

        for i in range(0, len(song_ids), 100):
            batch = song_ids[i : i + 100]
            ids_str = ",".join(str(sid) for sid in batch)
            detail_resp = await self._client.get("/song/detail", params={"ids": ids_str})
            detail_data = detail_resp.json()

            db = await get_db()
            for song in detail_data.get("songs", []):
                artists = ", ".join(a["name"] for a in song.get("artists", []))
                artist_ids = ", ".join(str(a["id"]) for a in song.get("artists", []))
                album = song.get("album", {})
                try:
                    await db.execute(
                        """INSERT OR REPLACE INTO liked_songs
                           (song_id, name, artist, album, added_at, synced_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            str(song["id"]),
                            song["name"],
                            artists,
                            album.get("name", ""),
                            now,
                            now,
                        ),
                    )
                    await db.execute(
                        """INSERT OR IGNORE INTO all_songs
                           (song_id, name, artist, artist_id, album, album_id, duration, source, created_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, 'netease', ?)""",
                        (
                            str(song["id"]),
                            song["name"],
                            artists,
                            artist_ids,
                            album.get("name", ""),
                            str(album.get("id", "")),
                            song.get("duration", 0),
                            now,
                        ),
                    )
                    for a in song.get("artists", []):
                        await db.execute(
                            """INSERT OR REPLACE INTO user_artists
                               (artist_id, artist_name, listen_count)
                               VALUES (?, ?, COALESCE((SELECT listen_count FROM user_artists WHERE artist_id=?), 0) + 1)""",
                            (str(a["id"]), a["name"], str(a["id"])),
                        )
                    synced += 1
                except Exception:
                    pass
            await db.commit()
            await db.close()

        return synced

    async def sync_playlists(self, uid: str, cookies: dict[str, str]) -> int:
        await self._ensure_client(cookies)
        resp = await self._client.get("/user/playlist", params={"uid": uid})
        data = resp.json()
        return len(data.get("playlist", []))

    async def sync_listen_history(self, uid: str, cookies: dict[str, str]) -> int:
        await self._ensure_client(cookies)
        resp = await self._client.get("/user/record", params={"uid": uid, "type": 0})
        data = resp.json()
        records = data.get("allData", [])
        synced = 0
        now = datetime.now().isoformat()

        db = await get_db()
        for record in records[:200]:
            song = record.get("song", {})
            play_count = record.get("score", 0)
            song_id = str(song.get("id", ""))
            if not song_id:
                continue
            artists = ", ".join(a["name"] for a in song.get("artists", []))
            try:
                await db.execute(
                    """INSERT OR IGNORE INTO all_songs
                       (song_id, name, artist, duration, source, created_at)
                       VALUES (?, ?, ?, ?, 'netease', ?)""",
                    (song_id, song.get("name", ""), artists, song.get("duration", 0), now),
                )
                for _ in range(min(play_count, 50)):
                    await db.execute(
                        "INSERT INTO listen_history (song_id, played_at, source) VALUES (?, ?, ?)",
                        (song_id, now, "history"),
                    )
                synced += 1
            except Exception:
                pass
        await db.commit()
        await db.close()
        return synced
