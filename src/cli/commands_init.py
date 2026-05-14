import asyncio

import click

from src.storage.config import load_config, get_config_path
from src.storage.database import init_db


@click.command()
@click.option("--force", is_flag=True, help="重新初始化")
def init(force: bool):
    """初始化项目（首次使用）"""

    async def _run():
        click.echo("🔧 正在初始化 AI 音乐伙伴...\n")

        await init_db()
        click.echo("✓ 数据库已初始化")

        cfg = load_config()
        name = cfg["personality"]["name"]
        click.echo(f"✓ AI 伙伴「{name}」已就绪")
        click.echo(f"✓ 配置文件: {get_config_path()}")

        has_key = bool(cfg["ai"].get("api_key"))
        if not has_key:
            click.echo("\n⚠️  未配置 API Key，聊天功能将使用模拟模式")
            click.echo("   建议配置 DeepSeek / OpenAI 的 API Key：")
            click.echo(           "   yinban config set ai.api_key sk-xxx")

        click.echo("\n✨ 初始化完成！试试这些命令：")
        click.echo("   yinban chat            # 和AI聊天")
        click.echo("   yinban recommend       # 获取推荐")
        click.echo("   yinban login           # 登录网易云同步数据")
        click.echo("   yinban config list     # 查看配置")

    asyncio.run(_run())
