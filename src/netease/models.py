from dataclasses import dataclass
from datetime import datetime


@dataclass
class Song:
    song_id: str
    name: str
    artist: str
    album: str = ""
    genre: str = ""
    duration: int = 0
    url: str = ""


@dataclass
class Playlist:
    playlist_id: str
    name: str
    song_count: int = 0
    songs: list[Song] | None = None


@dataclass
class User:
    user_id: str
    nickname: str
    avatar_url: str = ""
