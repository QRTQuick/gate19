"""Git helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from gate19.utils.console import console, info, warning


def init_git(project_root: Path) -> bool:
    """Initialize git repo if not already."""
    if (project_root / ".git").exists():
        return False
    try:
        result = subprocess.run(
            ["git", "init", str(project_root)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            warning(f"git init failed: {result.stderr.strip()[:200]}")
            return False
        # initial commit? create .gitkeep behavior
        # set default branch? not needed
        console.print("[green]  ✓ Git repository initialized[/]")
        return True
    except FileNotFoundError:
        warning("git not found on PATH — skipping git init")
        return False
    except Exception as e:
        warning(f"git init error: {e}")
        return False


def git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=5)
        return True
    except Exception:
        return False
