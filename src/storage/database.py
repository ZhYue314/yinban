from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).parent.parent.parent / "data" / "database.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS liked_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT UNIQUE,
    name TEXT,
    artist TEXT,
    album TEXT,
    genre TEXT,
    added_at TIMESTAMP,
    synced_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS listen_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT,
    played_at TIMESTAMP,
    source TEXT
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT,
    reason TEXT,
    user_feedback INTEGER,
    recommended_at TIMESTAMP,
    mood TEXT,
    scene TEXT
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    message TEXT,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    value TEXT,
    confidence REAL DEFAULT 1.0,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_state_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE,
    mood TEXT,
    energy TEXT,
    summary TEXT
);

CREATE TABLE IF NOT EXISTS all_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT UNIQUE,
    name TEXT,
    artist TEXT,
    artist_id TEXT,
    album TEXT,
    album_id TEXT,
    genre TEXT,
    duration INTEGER,
    popularity INTEGER DEFAULT 0,
    source TEXT DEFAULT 'netease',
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS similar_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_song_id TEXT,
    to_song_id TEXT,
    similarity REAL,
    reason TEXT,
    UNIQUE(from_song_id, to_song_id)
);

CREATE TABLE IF NOT EXISTS user_artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_id TEXT UNIQUE,
    artist_name TEXT,
    listen_count INTEGER DEFAULT 0,
    last_listened TIMESTAMP
);
"""


async def get_db() -> aiosqlite.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    db = await get_db()
    for statement in SCHEMA.split(";"):
        statement = statement.strip()
        if statement:
            await db.execute(statement)
    await db.commit()
    await db.close()
