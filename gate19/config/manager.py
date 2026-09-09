"""gate19.toml configuration manager."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore

try:
    import tomli_w  # type: ignore

    HAS_TOMLI_W = True
except ImportError:
    HAS_TOMLI_W = False

from gate19.utils.console import warning

DEFAULT_CONFIG = {
    "python": "3.11",
    "template": "app",
    "auto_install": True,
    "auto_format": True,
    "auto_test": False,
}


@dataclass
class CacheConfig:
    enabled: bool = True
    dir: str = "~/.cache/gate19"
    ttl: int = 3600


@dataclass
class ResolverConfig:
    parallel: bool = True
    cache_ttl: int = 3600
    max_workers: int = 8


@dataclass
class Config:
    python: str = "3.11"
    template: str = "app"
    auto_install: bool = True
    auto_format: bool = True
    auto_test: bool = False
    cache: CacheConfig = field(default_factory=CacheConfig)
    resolver: ResolverConfig = field(default_factory=ResolverConfig)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        cache_data = data.get("cache", {})
        resolver_data = data.get("resolver", {})
        return cls(
            python=str(data.get("python", "3.11")),
            template=str(data.get("template", "app")),
            auto_install=bool(data.get("auto_install", True)),
            auto_format=bool(data.get("auto_format", True)),
            auto_test=bool(data.get("auto_test", False)),
            cache=CacheConfig(
                enabled=bool(cache_data.get("enabled", True)),
                dir=str(cache_data.get("dir", "~/.cache/gate19")),
                ttl=int(cache_data.get("ttl", 3600)),
            ),
            resolver=ResolverConfig(
                parallel=bool(resolver_data.get("parallel", True)),
                cache_ttl=int(resolver_data.get("cache_ttl", 3600)),
                max_workers=int(resolver_data.get("max_workers", 8)),
            ),
            raw=data,
        )


def get_gate19_toml_path(start: Path | None = None) -> Path | None:
    cur = (start or Path.cwd()).resolve()
    for parent in [cur, *cur.parents]:
        cand = parent / "gate19.toml"
        if cand.exists():
            return cand
    return None


def load_config(project_root: Path | None = None) -> Config:
    """Load gate19.toml from project root or cwd, with env overrides."""
    root = project_root or Path.cwd()
    toml_path = root / "gate19.toml"
    if not toml_path.exists():
        # try find up
        found = get_gate19_toml_path(root)
        if found:
            toml_path = found
        else:
            # no config, use defaults + env
            data: dict[str, Any] = dict(DEFAULT_CONFIG)
            _apply_env_overrides(data)
            return Config.from_dict(data)

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        warning(f"Failed to parse {toml_path}: {e}, using defaults")
        data = dict(DEFAULT_CONFIG)

    # flatten? gate19.toml may have top-level keys as per spec example
    # ensure defaults
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    _apply_env_overrides(merged)
    return Config.from_dict(merged)


def _apply_env_overrides(data: dict[str, Any]) -> None:
    # GATE19_PYTHON, GATE19_TEMPLATE etc
    for key in ["python", "template"]:
        env = os.getenv(f"GATE19_{key.upper()}")
        if env:
            data[key] = env
    for bool_key in ["auto_install", "auto_format", "auto_test"]:
        env = os.getenv(f"GATE19_{bool_key.upper()}")
        if env is not None:
            data[bool_key] = env.lower() in ("1", "true", "yes", "on")


def write_default_config(project_root: Path, python: str = "3.11", template: str = "app") -> Path:
    path = project_root / "gate19.toml"
    content = f'''# Gate19 Configuration
python = "{python}"
template = "{template}"
auto_install = true
auto_format = true
auto_test = false

[cache]
enabled = true
dir = "~/.cache/gate19"
ttl = 3600

[resolver]
parallel = true
cache_ttl = 3600
max_workers = 8
'''
    path.write_text(content, encoding="utf-8")
    return path
