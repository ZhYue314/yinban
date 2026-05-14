import asyncio

import click

from src.core.personality import Personality
from src.storage.database import get_db


@click.command()
def discover():
    """发现新歌手"""

    async def _run():
        personality = Personality()
        click.echo(f"🔍 {personality.name} 正在帮你发现新歌手...\n")

        db = await get_db()

        cursor = await db.execute(
            "SELECT artist_name, listen_count FROM user_artists ORDER BY listen_count DESC LIMIT 10"
        )
        liked_artists = await cursor.fetchall()

        if not liked_artists:
            click.echo("还没有数据，请先运行 login 同步网易云数据")
            await db.close()
            return

        click.echo("你常听的歌手:")
        for a in liked_artists:
            click.echo(f"  • {a['artist_name']} ({a['listen_count']} 次)")

        liked_names = [a["artist_name"] for a in liked_artists]

        click.echo(f"\n{personality.name} 觉得你可能也会喜欢这些:\n")

        discoveries = [
            ("风格相似", "独立摇滚"),
            ("情感共鸣", "后摇/氛围音乐"),
            ("经典延续", "同时代的创作歌手"),
        ]

        for reason, style in discoveries:
            click.echo(f"  基于「{reason}」→ 试试 {style}")

        await db.close()

    asyncio.run(_run())
