"""Configuration loading: ``config.yaml`` merged with CLI overrides."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class Config:
    base_url: str = "https://en.wikipedia.org/w/api.php"
    rest_base_url: str = "https://wikimedia.org/api/rest_v1"
    user_agent: str = "lexphon/0.1 (https://github.com/xenotropic/lexphon)"
    api_chunk_size: int = 50
    rate_limit_sleep: float = 0.0
    timeout: int = 30
    max_retries: int = 3
    vital_level: int = 1
    popular_limit: int = 0
    popularity_timeframe: str = "last-month"
    min_pageviews: int = 0
    titles: list[str] = field(default_factory=list)
    low_memory: bool = True


def load_config(path: str | None, overrides: dict[str, Any] | None = None) -> Config:
    """Load ``config.yaml`` (all keys optional) and overlay ``overrides``.

    Only keys explicitly present in ``overrides`` (non-``None`` values) win.
    Unknown keys raise ``ValueError`` so typos fail loudly.
    """
    data: dict[str, Any] = {}
    if path is not None:
        with open(path, "r", encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"config file {path!r} must contain a YAML mapping")
        data = loaded

    data.update({k: v for k, v in (overrides or {}).items() if v is not None})

    known = set(Config.__dataclass_fields__)
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"unknown config keys: {sorted(unknown)}")

    return Config(**data)