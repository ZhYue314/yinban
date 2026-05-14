import asyncio
import json
from pathlib import Path

import click
import httpx

from src.netease.auth import NeteaseAuth
from src.netease.client import NeteaseClient
from src.netease.sync import NeteaseSync
from src.storage.config import load_config, save_config
from src.storage.database import get_db

COOKIE_PATH = Path(__file__).parent.parent.parent / "data" / ".netease_cookies"


def _save_cookies(cookies: dict[str, str]):
    COOKIE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(COOKIE_PATH, "w") as f:
        json.dump(cookies, f)


def _load_cookies() -> dict[str, str]:
    if COOKIE_PATH.exists():
        with open(COOKIE_PATH) as f:
            return json.load(f)
    return {}


@click.command()
def login():
    """登录网易云音乐"""

    async def _run():
        click.echo("🔌 检查网易云 API 服务...")
        sync = NeteaseSync()
        if not await sync.health_check():
            click.echo(
                "❌ 未检测到网易云 API 服务\n\n"
                "需要先启动 NeteaseCloudMusicApi 服务：\n"
                "  1. git clone https://github.com/Binaryify/NeteaseCloudMusicApi\n"
                "  2. cd NeteaseCloudMusicApi && npm install && node app.js\n"
                "  3. 保持服务运行在 localhost:3000\n"
            )
            return
        await sync.close()

        click.echo("📱 正在生成二维码...")
        client = NeteaseClient()
        auth = NeteaseAuth(client)
        result = await auth.login_by_qrcode()

        if not result:
            click.echo("❌ 登录失败")
            return

        account = result.get("account") or result.get("profile", {})
        uid = str(account.get("userId", account.get("uid", "")))
        nickname = account.get("nickname", "")

        cfg = load_config()
        cfg["netease"]["uid"] = uid
        cfg["netease"]["nickname"] = nickname
        save_config(cfg)

        cookies = client.get_cookies()
        _save_cookies(cookies)

        click.echo(f"\n✅ 登录成功！欢迎 {nickname}")

        click.echo("\n📥 正在同步数据...")
        await _sync_data(uid, cookies)

        await client.close()

    asyncio.run(_run())


@click.command()
def logout():
    """退出网易云登录"""

    def _run():
        if COOKIE_PATH.exists():
            COOKIE_PATH.unlink()
        cfg = load_config()
        cfg["netease"]["uid"] = ""
        cfg["netease"]["nickname"] = ""
        save_config(cfg)
        click.echo("✅ 已退出登录")

    _run()


@click.command()
def sync():
    """同步网易云数据"""

    async def _run():
        cfg = load_config()
        uid = cfg.get("netease", {}).get("uid", "")
        if not uid:
            click.echo("❌ 未登录，请先运行 login")
            return

        cookies = _load_cookies()
        if not cookies:
            click.echo("❌ 登录态已过期，请重新运行 login")
            return

        click.echo("🔌 检查服务...")
        sync = NeteaseSync()
        if not await sync.health_check():
            click.echo("❌ API 服务未启动")
            return

        await _sync_data(uid, cookies)
        await sync.close()

    asyncio.run(_run())


async def _sync_data(uid: str, cookies: dict[str, str]):
    sync = NeteaseSync()

    click.echo("  🎵 同步喜欢的音乐...")
    liked = await sync.sync_liked_songs(uid, cookies)
    click.echo(f"     ✓ 已同步 {liked} 首喜欢的歌曲")

    click.echo("  📋 同步听歌记录...")
    history = await sync.sync_listen_history(uid, cookies)
    click.echo(f"     ✓ 已同步 {history} 条听歌记录")

    await sync.close()

    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) as c FROM all_songs")
    total = (await cursor.fetchone())["c"]
    cursor = await db.execute("SELECT COUNT(*) as c FROM user_artists")
    artists = (await cursor.fetchone())["c"]
    await db.close()

    click.echo(f"\n📊 数据概览: {total} 首歌曲, {artists} 位歌手")
