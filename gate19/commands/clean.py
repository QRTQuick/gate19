"""gate19 clean — project cleaner."""

from __future__ import annotations

import shutil
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.cache.manager import CacheManager
from gate19.utils.console import console, success, info, warning
from gate19.utils.fs import find_project_root

TARGETS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "htmlcov",
    "dist",
    "build",
    "*.egg-info",
]

@app.command("clean")
def clean_command(
    all: bool = typer.Option(False, "--all", "-a", help="Also remove .venv and caches"),
    venv: bool = typer.Option(False, "--venv", help="Remove virtual environment"),
    cache: bool = typer.Option(False, "--cache", help="Clear Gate19 cache"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed"),
):
    """Clean project artifacts and caches. 🧹"""
    root = find_project_root() or Path.cwd()
    info(f"Cleaning project at {root}...")

    removed = []

    # Find __pycache__ etc
    patterns = ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis", "htmlcov", ".coverage*"]
    for pattern in patterns:
        for p in root.rglob(pattern):
            # only if within root and not inside .venv unless --all
            if ".venv" in p.parts and not all:
                continue
            if p.exists():
                removed.append(p)
                if not dry_run:
                    try:
                        if p.is_dir():
                            shutil.rmtree(p, ignore_errors=True)
                        else:
                            p.unlink(missing_ok=True)
                    except Exception:
                        pass

    # dist, build, egg-info at root
    for name in ["dist", "build"]:
        p = root / name
        if p.exists():
            removed.append(p)
            if not dry_run:
                shutil.rmtree(p, ignore_errors=True)
    for p in root.glob("*.egg-info"):
        removed.append(p)
        if not dry_run:
            shutil.rmtree(p, ignore_errors=True)

    # .venv
    if all or venv:
        venv_path = root / ".venv"
        if venv_path.exists():
            removed.append(venv_path)
            if not dry_run:
                shutil.rmtree(venv_path, ignore_errors=True)

    # Gate19 cache
    if all or cache:
        cm = CacheManager()
        count = 0 if dry_run else cm.clear()
        if dry_run:
            info("Would clear Gate19 cache")
        else:
            info(f"Cleared {count} cache entries")

    if dry_run:
        if not removed:
            console.print("[dim]Nothing to clean[/]")
        else:
            console.print("[yellow]Would remove:[/]")
            for p in removed[:50]:
                console.print(f"  • {p.relative_to(root) if p.is_relative_to(root) else p}")
            if len(removed) > 50:
                console.print(f"  ... and {len(removed)-50} more")
    else:
        if not removed:
            console.print("[dim]Nothing to clean — project already tidy[/]")
        else:
            success(f"Cleaned {len(removed)} paths ✓")
            for p in removed[:20]:
                console.print(f"[dim]  • {p}[/]")
