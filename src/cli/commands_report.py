import asyncio
from datetime import date, timedelta

import click

from src.core.init import ensure_db
from src.core.personality import Personality
from src.storage.database import get_db


@click.command()
@click.option("--period", "-p", default="weekly", help="报告周期: weekly/monthly")
def report(period: str):
    """生成听歌报告"""

    async def _run():
        await ensure_db()
        personality = Personality()

        db = await get_db()
        try:
            c = await db.execute("SELECT COUNT(*) as c FROM liked_songs")
            liked = (await c.fetchone())["c"]

            c = await db.execute("SELECT COUNT(*) as c FROM all_songs")
            total = (await c.fetchone())["c"]

            c = await db.execute("SELECT COUNT(*) as c FROM user_artists")
            artists = (await c.fetchone())["c"]

            c = await db.execute("SELECT artist_name, listen_count FROM user_artists ORDER BY listen_count DESC LIMIT 5")
            top_artists = await c.fetchall()

            c = await db.execute("SELECT COUNT(*) as c FROM chat_history WHERE role='user'")
            chats = (await c.fetchone())["c"]

            c = await db.execute("SELECT value FROM memories WHERE key='likes_genre' ORDER BY updated_at DESC LIMIT 5")
            genres = await c.fetchall()

            click.echo(f"📊 {personality.name} 的{period}报告\n")
            click.echo(f"🎵 音乐数据")
            click.echo(f"  收藏歌曲: {liked} 首")
            click.echo(f"  总共入库: {total} 首")
            click.echo(f"  听过的歌手: {artists} 位")

            if top_artists:
                click.echo(f"\n🏆 最常听歌手 TOP5")
                for i, a in enumerate(top_artists, 1):
                    click.echo(f"  {i}. {a['artist_name']} ({a['listen_count']})")

            if genres:
                click.echo(f"\n🎯 你的音乐风格")
                for g in genres:
                    click.echo(f"  • {g['value']}")

            click.echo(f"\n💬 聊天")
            click.echo(f"  总共聊了 {chats} 条消息")
            click.echo(f"  亲密度: {personality.closeness:.2f}")

            days_known = int(personality.closeness * 100)
            click.echo(f"  认识 {personality.name} 大概 {days_known} 天了")

        finally:
            await db.close()

    asyncio.run(_run())
