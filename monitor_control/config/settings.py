from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Settings:
    raw: dict[str, Any]


def default_config_path() -> Path:
    return Path.home() / ".config" / "monitor_control" / "config.yaml"


def load_settings(path: Path | None = None) -> Settings:
    p = path or default_config_path()
    if not p.exists():
        return Settings(raw={})
    with p.open("r", encoding="utf-8") as f:
        return Settings(raw=yaml.safe_load(f) or {})
