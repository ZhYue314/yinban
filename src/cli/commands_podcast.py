import asyncio
from datetime import date

import click

from src.ai.llm import LLMClient
from src.core.init import ensure_db
from src.core.personality import Personality
from src.core.recommender import Recommender
from src.podcast.script import ScriptGenerator
from src.podcast.tts import TTSEngine
from src.storage.database import get_db


@click.command()
@click.option("--type", "ptype", default="daily", help="播客类型: daily/recommend")
@click.option("--voice", default="zh-CN-XiaoxiaoNeural", help="语音角色")
@click.option("--mood", "-m", help="按心情生成播客")
@click.option("--scene", "-s", help="按场景生成播客")
@click.option("--no-tts", is_flag=True, help="仅输出文字，不合成语音")
def podcast(ptype: str, voice: str, mood: str | None, scene: str | None, no_tts: bool):
    """生成语音播客"""

    async def _run():
        await ensure_db()
        personality = Personality()
        llm = LLMClient()
        recommender = Recommender(personality)
        script_gen = ScriptGenerator(personality, llm)
        tts = TTSEngine(voice)

        if mood:
            songs = await recommender.recommend_by_mood(mood, 5)
            click.echo(f"🎙️ 根据心情「{mood}」生成播客...")
            script = await script_gen.generate_recommend_script(songs, mood)
        elif scene:
            songs = await recommender.recommend_by_scene(scene, 5)
            click.echo(f"🎙️ 根据场景「{scene}」生成播客...")
            script = await script_gen.generate_recommend_script(songs)
        else:
            songs = await recommender.recommend_from_liked(5)
            click.echo(f"🎙️ 生成每日播客...")
            script = await script_gen.generate_daily_script(songs)

        click.echo(f"\n📝 {personality.name} 的播客内容:\n")
        click.echo(script)
        click.echo()

        if not no_tts:
            click.echo(f"🔊 正在用「{voice}」合成语音...")
            today = date.today().isoformat()
            filename = f"podcast_{today}.mp3"
            output_path = await tts.speak(script, filename)
            click.echo(f"✅ 播客已保存: {output_path}")
        else:
            click.echo("（--no-tts 跳过语音合成）")

    asyncio.run(_run())
