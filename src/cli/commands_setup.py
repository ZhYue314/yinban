import asyncio

import click

from src.storage.config import load_config, save_config


@click.command()
def setup():
    """交互式配置向导"""

    async def _run():
        cfg = load_config()

        click.echo("╔══════════════════════════════╗")
        click.echo("║    音 伴 配 置 向 导        ║")
        click.echo("╚══════════════════════════════╝")
        click.echo()
        click.echo("按 Enter 跳过，保持当前值\n")

        # === AI 配置 ===
        click.echo("── AI 配置 ──")
        current = cfg["ai"].get("api_key", "")
        masked = current[:8] + "****" if len(current) > 8 else "(未设置)"
        val = click.prompt(f"API Key [{masked}]", default="", show_default=False)
        if val:
            cfg["ai"]["api_key"] = val
            click.echo("  ✓ API Key 已设置")

        current = cfg["ai"].get("provider", "deepseek")
        val = click.prompt(f"API 提供商 [{current}]", default=current)
        if val:
            cfg["ai"]["provider"] = val

        current = cfg["ai"].get("model", "deepseek-chat")
        val = click.prompt(f"模型 [{current}]", default=current)
        if val:
            cfg["ai"]["model"] = val

        # === 人格配置 ===
        click.echo("\n── AI 人格配置 ──")
        current = cfg["personality"].get("name", "小野")
        val = click.prompt(f"AI 名字 [{current}]", default=current)
        if val:
            cfg["personality"]["name"] = val

        current = cfg["personality"].get("tone", "毒舌")
        val = click.prompt(
            f"性格基调 [{current}]",
            default=current,
        )
        if val:
            cfg["personality"]["tone"] = val

        current = cfg["personality"].get("bio", "")
        val = click.prompt(f"一句话简介 [{current}]", default=current)
        if val:
            cfg["personality"]["bio"] = val

        # === 品味配置 ===
        click.echo("\n── 音乐品味配置 ──")
        current = cfg["taste"].get("stubbornness", 0.5)
        val = click.prompt(
            f"坚持己见程度 0~1 [{current}]",
            default=str(current),
        )
        if val:
            try:
                cfg["taste"]["stubbornness"] = float(val)
            except ValueError:
                click.echo("  跳过（无效数字）")

        save_config(cfg)
        click.echo("\n✅ 配置已保存！")

        has_key = bool(cfg["ai"].get("api_key"))
        if not has_key:
            click.echo("\n⚠️  未设置 API Key，聊天将使用模拟模式")

        click.echo("\n试试这些命令：")
        click.echo("  python main.py chat")
        click.echo("  python main.py recommend")
        click.echo("  python main.py config list")

    asyncio.run(_run())
