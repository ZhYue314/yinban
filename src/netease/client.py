import asyncio
from typing import Any

import httpx


class NeteaseClient:
    BASE_URL = "http://localhost:3000"

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or self.BASE_URL
        self._client: httpx.AsyncClient | None = None
        self._cookies: dict[str, str] = {}

    async def _ensure_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                cookies=self._cookies,
                timeout=30.0,
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        await self._ensure_client()
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        await self._ensure_client()
        resp = await self._client.post(path, json=data)
        resp.raise_for_status()
        return resp.json()

    async def login_qrcode_key(self) -> dict[str, Any]:
        return await self._get("/login/qr/key")

    async def login_qrcode_create(self, key: str) -> dict[str, Any]:
        return await self._get("/login/qr/create", params={"key": key, "qrimg": True})

    async def login_qrcode_check(self, key: str) -> dict[str, Any]:
        return await self._get("/login/qr/check", params={"key": key})

    async def login_cellphone(self, phone: str, captcha: str) -> dict[str, Any]:
        return await self._get("/login/cellphone", params={"phone": phone, "captcha": captcha})

    async def get_liked_songs(self, uid: str, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        return await self._get("/likelist", params={"uid": uid})

    async def get_user_playlists(self, uid: str) -> dict[str, Any]:
        return await self._get("/user/playlist", params={"uid": uid})

    async def get_playlist_detail(self, playlist_id: str) -> dict[str, Any]:
        return await self._get("/playlist/detail", params={"id": playlist_id})

    async def get_song_detail(self, song_id: str) -> dict[str, Any]:
        return await self._get("/song/detail", params={"ids": song_id})

    async def get_song_url(self, song_id: str) -> dict[str, Any]:
        return await self._get("/song/url", params={"id": song_id})

    async def get_recommend_songs(self) -> dict[str, Any]:
        return await self._get("/recommend/songs")

    async def get_user_record(self, uid: str, record_type: int = 0) -> dict[str, Any]:
        return await self._get("/user/record", params={"uid": uid, "type": record_type})

    async def search(self, keyword: str, search_type: int = 1) -> dict[str, Any]:
        return await self._get("/search", params={"keywords": keyword, "type": search_type})

    async def get_song_comments(self, song_id: str, limit: int = 20) -> dict[str, Any]:
        return await self._get("/comment/music", params={"id": song_id, "limit": limit})

    async def get_lyric(self, song_id: str) -> dict[str, Any]:
        return await self._get("/lyric", params={"id": song_id})

    async def get_top_songs(self, idx: int = 0) -> dict[str, Any]:
        return await self._get("/top/song", params={"idx": idx})

    async def get_personal_fm(self) -> dict[str, Any]:
        return await self._get("/personal_fm")

    async def like_song(self, song_id: str, like: bool = True) -> dict[str, Any]:
        return await self._get("/like", params={"id": song_id, "like": "true" if like else "false"})

    def get_cookies(self) -> dict[str, str]:
        if self._client:
            return dict(self._client.cookies)
        return {}
