import click

from .commands_chat import chat
from .commands_recommend import recommend, daily
from .commands_podcast import podcast
from .commands_config import config
from .commands_init import init


@click.group()
@click.version_option(version="0.1.0", prog_name="ai-podcast")
def cli():
    """AI 音乐伙伴 - 住在你电脑里的音乐朋友"""


cli.add_command(chat)
cli.add_command(recommend)
cli.add_command(daily)
cli.add_command(podcast)
cli.add_command(config)
cli.add_command(init)


if __name__ == "__main__":
    cli()
