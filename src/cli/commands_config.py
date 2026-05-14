import click

from src.storage.config import load_config, save_config, get_config_path, DEFAULT_CONFIG


@click.group()
def config():
    """查看或修改配置"""


@config.command("list")
def list_config():
    """查看所有配置"""
    cfg = load_config()
    click.echo(f"配置文件路径: {get_config_path()}\n")

    def _print_section(name: str, data: dict):
        click.echo(f"[{name}]")
        for k, v in data.items():
            click.echo(f"  {k} = {v}")
        click.echo()

    _print_section("personality", cfg["personality"])
    _print_section("taste", cfg["taste"])
    _print_section("state", cfg["state"])
    _print_section("relationship", cfg["relationship"])
    _print_section("ai", cfg["ai"])
    _print_section("netease", cfg["netease"])


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """修改配置，如: config set personality.name 小野"""
    cfg = load_config()
    parts = key.split(".", 1)

    if len(parts) == 2:
        section, field = parts
        if section in cfg and field in cfg[section]:
            current = cfg[section][field]
            if isinstance(current, bool):
                cfg[section][field] = value.lower() in ("true", "1", "yes")
            elif isinstance(current, int):
                cfg[section][field] = int(value)
            elif isinstance(current, float):
                cfg[section][field] = float(value)
            elif isinstance(current, list):
                cfg[section][field] = [v.strip() for v in value.split(",")]
            else:
                cfg[section][field] = value
            save_config(cfg)
            click.echo(f"✓ {key} = {cfg[section][field]}")
        else:
            click.echo(f"❌ 无效配置项: {key}")
    else:
        click.echo("格式: config set <section.field> <value>")


@config.command()
def reset():
    """恢复默认配置"""
    save_config(dict(DEFAULT_CONFIG))
    click.echo("✓ 已恢复默认配置")
