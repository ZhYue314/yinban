import asyncio

import click

from src.ai.llm import LLMClient
from src.core.personality import Personality
from src.podcast.script import ScriptGenerator
from src.podcast.tts import TTSEngine


@click.command()
@click.option("--type", "podcast_type", default="daily", help="播客类型: daily/recommend")
@click.option("--voice", default="zh-CN-XiaoxiaoNeural", help="语音角色")
def podcast(podcast_type: str, voice: str):
    """生成语音播客"""

    async def _run():
        personality = Personality()
        llm = LLMClient()
        script_gen = ScriptGenerator(personality, llm)
        tts = TTSEngine(voice)

        click.echo(f"🎙️ 正在生成播客脚本...")
        script = await script_gen.generate_daily_script([])

        click.echo(f"📝 播客内容:\n{script}\n")
        click.echo(f"🔊 正在合成语音...")

        output_path = await tts.speak(script)
        click.echo(f"✅ 播客已生成: {output_path}")

    asyncio.run(_run())
