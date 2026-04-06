"""User configuration persistence for LAN Messenger."""

import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".lan_messenger"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Load saved configuration. Returns empty dict if none exists."""
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_config(name: str = "", server_ip: str = "", server_port: int = 0) -> None:
    """Save configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = load_config()
    if name:
        config["name"] = name
    if server_ip:
        config["server_ip"] = server_ip
    if server_port:
        config["server_port"] = server_port
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
