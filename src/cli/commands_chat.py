import asyncio

import click

from src.ai.llm import LLMClient
from src.core.chat import ChatEngine
from src.core.init import ensure_db
from src.core.personality import Personality
from src.storage.database import get_db


@click.command()
@click.option("--one-shot", "-o", help="发送单条消息后退出")
def chat(one_shot: str | None):
    """和你的AI音乐伙伴聊天"""

    async def _run(message: str | None = None):
        await ensure_db()
        personality = Personality()
        llm = LLMClient()
        engine = ChatEngine(personality, llm)

        if message:
            reply = await engine.chat(message)
            click.echo(f"\n{personality.name}: {reply}")
            return

        click.echo(f"\n💬 和 {personality.name} 聊天开始（输入 /quit 退出）")
        click.echo(f"    /mood <心情>  /rename <名字>  /stats  /recommend\n")

        while True:
            user_input = click.prompt("你", prompt_suffix=" > ")
            if user_input.lower() in ("/quit", "/exit", "/q"):
                break
            if user_input.startswith("/"):
                await _handle_slash(user_input, personality, engine)
                continue

            reply = await engine.chat(user_input)
            click.echo(f"\n{personality.name}: {reply}\n")

    asyncio.run(_run(one_shot))


async def _handle_slash(cmd: str, personality: Personality, engine: ChatEngine):
    parts = cmd.split(maxsplit=1)
    action = parts[0].lower()

    if action == "/mood":
        if len(parts) > 1:
            personality.today_mood = parts[1]
            personality.save()
            click.echo(f"✓ 心情已设置为: {parts[1]}")
        else:
            click.echo(f"当前心情: {personality.today_mood} | 精力: {personality.energy}")
    elif action == "/rename":
        if len(parts) > 1:
            old = personality.name
            personality.name = parts[1]
            personality.save()
            click.echo(f"✓ 已从 {old} 改名为 {parts[1]}")
    elif action == "/stats":
        db = await get_db()
        try:
            c = await db.execute("SELECT COUNT(*) as c FROM chat_history WHERE role='user'")
            msgs = (await c.fetchone())["c"]
            c = await db.execute("SELECT COUNT(*) as c FROM liked_songs")
            songs = (await c.fetchone())["c"]
            click.echo(f"聊天消息: {msgs} 条")
            click.echo(f"收藏歌曲: {songs} 首")
            click.echo(f"亲密度: {personality.closeness:.2f}")
            click.echo(f"性格: {personality.tone}")
        finally:
            await db.close()
    elif action == "/recommend":
        from src.core.recommender import Recommender
        r = Recommender(personality)
        recs = await r.recommend_from_liked(3)
        if recs:
            click.echo(f"{personality.name} 说：给你推几首——")
            for s in recs:
                label = f"{s['name']} - {s['artist']}" if s["artist"] else s["name"]
                click.echo(f"  • {label}")
        else:
            click.echo("还没有数据，先 login 同步吧")
    else:
        click.echo("可用命令: /mood, /rename, /stats, /recommend, /quit")
