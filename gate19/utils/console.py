"""Rich console helpers with icons and colors."""

from __future__ import annotations

import sys
from typing import Any

from rich.console import Console
from rich.theme import Theme

_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "muted": "dim",
        "accent": "bold magenta",
    }
)

console = Console(theme=_theme, highlight=True)

ICONS = {
    "success": "✓",
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
    "arrow": "→",
    "rocket": "🚀",
    "package": "📦",
    "sparkles": "✨",
    "wrench": "🔧",
    "check": "✔",
    "cross": "✘",
    "star": "★",
    "fire": "🔥",
    "zap": "⚡",
    "gear": "⚙",
}


def _print(icon: str, msg: str, style: str = "") -> None:
    console.print(f"{icon} {msg}", style=style)


def success(msg: str) -> None:
    _print(f"[success]{ICONS['success']}[/]", msg, "success")


def error(msg: str) -> None:
    _print(f"[error]{ICONS['error']}[/]", msg, "error")


def warning(msg: str) -> None:
    _print(f"[warning]{ICONS['warning']}[/]", msg, "warning")


def info(msg: str) -> None:
    _print(f"[info]{ICONS['info']}[/]", msg, "info")


def step(msg: str) -> None:
    _print(f"[accent]{ICONS['arrow']}[/]", msg, "accent")


def print_error_and_exit(msg: str, code: int = 1) -> None:
    error(msg)
    raise SystemExit(code)


def banner() -> None:
    console.print(
        "[bold magenta]Gate19[/] [dim]— The Next Generation Python Project Manager[/] [bold yellow]⚡[/]",
    )
