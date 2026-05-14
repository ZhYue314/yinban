from pathlib import Path


async def ensure_db():
    db_path = Path(__file__).parent.parent.parent / "data" / "database.sqlite"
    if not db_path.exists():
        from src.storage.database import init_db
        await init_db()
