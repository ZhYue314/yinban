import locale
import sys

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from src.cli.app import cli

if __name__ == "__main__":
    cli()
