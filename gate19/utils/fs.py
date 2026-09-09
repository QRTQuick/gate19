"""Filesystem helpers."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Union

StrPath = Union[str, os.PathLike[str]]


def ensure_dir(path: StrPath) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_file(path: StrPath, content: str, encoding: str = "utf-8") -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)
    return p


def read_file(path: StrPath, encoding: str = "utf-8") -> str:
    return Path(path).read_text(encoding=encoding)


def remove_dir(path: StrPath) -> None:
    p = Path(path)
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up to find pyproject.toml or gate19.toml or .git."""
    cur = (start or Path.cwd()).resolve()
    for parent in [cur, *cur.parents]:
        if (parent / "pyproject.toml").exists() or (parent / "gate19.toml").exists() or (parent / ".git").exists():
            return parent
    return None


def is_project_root(path: Path) -> bool:
    return (path / "pyproject.toml").exists()
