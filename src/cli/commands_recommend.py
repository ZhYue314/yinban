import asyncio

import click

from src.ai.llm import LLMClient
from src.core.init import ensure_db
from src.core.personality import Personality
from src.core.recommender import Recommender
from src.storage.database import get_db


@click.command()
@click.option("--mood", "-m", help="按心情推荐（开心/平静/伤感/烦躁/慵懒/热情）")
@click.option("--scene", "-s", help="按场景推荐（深夜/学习/跑步/通勤/工作）")
@click.option("--count", "-n", default=5, help="推荐数量")
def recommend(mood: str | None, scene: str | None, count: int):
    """推荐歌曲"""

    async def _run():
        await ensure_db()
        personality = Personality()
        recommender = Recommender(personality)

        if mood:
            click.echo(f"🎵 {personality.name} 知道你心情「{mood}」:\n")
            songs = await recommender.recommend_by_mood(mood, count)
            if not songs:
                click.echo("  还没有数据，先运行 login 同步歌曲吧")
            for s in songs:
                label = s["name"]
                if s["artist"]:
                    label += f" - {s['artist']}"
                click.echo(f"  • {label}")
                click.echo(f"    {s['reason']}\n")

        elif scene:
            click.echo(f"🎵 {personality.name} 觉得「{scene}」的时候适合听:\n")
            songs = await recommender.recommend_by_scene(scene, count)
            if not songs:
                click.echo("  还没有数据，先运行 login 同步歌曲吧")
            for s in songs:
                label = s["name"]
                if s["artist"]:
                    label += f" - {s['artist']}"
                click.echo(f"  • {label}")
                click.echo(f"    {s['reason']}\n")

        else:
            click.echo(f"🎵 {personality.name} 根据你的收藏推荐:\n")
            songs = await recommender.recommend_from_liked(count)
            db = await get_db()
            cursor = await db.execute("SELECT COUNT(*) as c FROM liked_songs")
            liked_count = (await cursor.fetchone())["c"]
            cursor = await db.execute("SELECT COUNT(*) as c FROM all_songs")
            total = (await cursor.fetchone())["c"]
            await db.close()

            click.echo(f"  你收藏了 {liked_count} 首歌曲，一共有 {total} 首入库\n")
            if not songs:
                click.echo("  还没有足够的数据，先运行 login 同步你的网易云数据吧")
            for s in songs:
                label = s["name"]
                if s["artist"]:
                    label += f" - {s['artist']}"
                click.echo(f"  • {label}")
                click.echo(f"    {s['reason']}\n")

    asyncio.run(_run())


@click.command()
@click.option("--count", "-n", default=5, help="推荐数量")
def daily(count: int):
    """每日推荐"""

    async def _run():
        await ensure_db()
        personality = Personality()
        recommender = Recommender(personality)
        result = await recommender.get_daily_recommendation()

        click.echo(f"📅 {personality.name} 的每日推荐")
        click.echo(f"今天心情: {result['mood']} | 精力: {result['energy']}\n")

        songs = result.get("songs", [])
        if songs:
            for s in songs:
                label = s["name"]
                if s["artist"]:
                    label += f" - {s['artist']}"
                click.echo(f"  • {label}")
                click.echo(f"    {s['reason']}\n")
        else:
            click.echo("  今天还没什么可推荐的，先运行 login 同步数据吧")

    asyncio.run(_run())
