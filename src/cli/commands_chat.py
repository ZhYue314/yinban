import asyncio

import click

from src.ai.llm import LLMClient
from src.core.chat import ChatEngine
from src.core.personality import Personality
from src.storage.config import load_config


@click.command()
@click.option("--one-shot", "-o", help="发送单条消息后退出")
def chat(one_shot: str | None):
    """和你的AI音乐伙伴聊天"""

    async def _run(message: str | None = None):
        from src.core.init import ensure_db
        await ensure_db()
        personality = Personality()
        llm = LLMClient()
        engine = ChatEngine(personality, llm)

        if message:
            reply = await engine.chat(message)
            click.echo(f"\n{personality.name}: {reply}")
            return

        click.echo(f"\n💬 和 {personality.name} 聊天开始（输入 /quit 退出）\n")

        while True:
            user_input = click.prompt("你", prompt_suffix=" > ")
            if user_input.lower() in ("/quit", "/exit", "/q"):
                break
            if user_input.startswith("/"):
                await _handle_slash(user_input, personality, llm, engine)
                continue

            reply = await engine.chat(user_input)
            click.echo(f"\n{personality.name}: {reply}\n")

    asyncio.run(_run(one_shot))


async def _handle_slash(cmd: str, personality: Personality, llm: LLMClient, engine: ChatEngine):
    parts = cmd.split(maxsplit=1)
    action = parts[0].lower()

    if action == "/mood":
        if len(parts) > 1:
            personality.today_mood = parts[1]
            personality.save()
            click.echo(f"✓ 情绪已设置为: {parts[1]}")
        else:
            click.echo(f"当前情绪: {personality.today_mood}")
    elif action == "/rename":
        if len(parts) > 1:
            personality.name = parts[1]
            personality.save()
            click.echo(f"✓ 已改名为: {parts[1]}")
    elif action == "/config":
        click.echo(f"亲密度: {personality.closeness:.2f}")
        click.echo(f"性格: {personality.tone}")
        click.echo(f"心情: {personality.today_mood}")
    else:
        click.echo("未知命令: /mood, /rename, /config, /quit")
