import asyncio

import click

from src.ai.llm import LLMClient
from src.core.personality import Personality
from src.core.recommender import Recommender


@click.command()
@click.option("--mood", "-m", help="按心情推荐")
@click.option("--scene", "-s", help="按场景推荐（如: 深夜/学习/跑步）")
@click.option("--count", "-n", default=5, help="推荐数量")
def recommend(mood: str | None, scene: str | None, count: int):
    """推荐歌曲"""

    async def _run():
        personality = Personality()
        recommender = Recommender(personality)

        if mood:
            result = await recommender.recommend_by_mood(mood, count)
            click.echo(f"🎵 {personality.name} 根据心情「{mood}」推荐:\n")
            click.echo(result.get("message", "暂无推荐"))
        elif scene:
            result = await recommender.recommend_by_scene(scene, count)
            click.echo(f"🎵 {personality.name} 根据场景「{scene}」推荐:\n")
            click.echo(result.get("message", "暂无推荐"))
        else:
            profile = await recommender.recommend_from_liked(count)
            click.echo(f"🎵 {personality.name} 根据你的收藏推荐:\n")
            click.echo(f"你的音乐画像:")
            click.echo(f"  歌手: {', '.join(profile['artists'][:5]) or '暂无'}")
            click.echo(f"  风格: {', '.join(profile['genres'][:5]) or '暂无'}")
            click.echo(f"  收藏: {profile['count']} 首")

    asyncio.run(_run())


@click.command()
@click.option("--count", "-n", default=5, help="推荐数量")
def daily(count: int):
    """每日推荐"""

    async def _run():
        personality = Personality()
        recommender = Recommender(personality)
        result = await recommender.get_daily_recommendation()
        click.echo(f"📅 {personality.name} 的每日推荐")
        click.echo(f"心情: {result['mood']} | 精力: {result['energy']}")

    asyncio.run(_run())
