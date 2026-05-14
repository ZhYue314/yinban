from pathlib import Path
from typing import Any

import yaml

CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "config.yaml"

DEFAULT_CONFIG = {
    "personality": {
        "name": "小野",
        "tone": "毒舌",
        "language_style": "简短",
        "bio": "有点毒舌但靠谱的音乐发烧友",
    },
    "taste": {
        "genre_preference": [],
        "era_preference": None,
        "stubbornness": 0.5,
        "discovery_ratio": 0.3,
    },
    "state": {
        "today_mood": "auto",
        "energy": "auto",
    },
    "relationship": {
        "closeness": 0.0,
        "nickname_for_user": "",
    },
    "ai": {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "api_key": "",
        "api_base": "",
    },
    "netease": {
        "phone": "",
        "cache_dir": "./data/cache",
    },
}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def get_config_path() -> Path:
    return CONFIG_PATH
