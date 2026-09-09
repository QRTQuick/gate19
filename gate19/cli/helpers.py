"""CLI helpers — shared utilities for commands."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional

import typer

from gate19.utils.console import error, console
from gate19.utils.fs import find_project_root

def require_project_root(start: Optional[Path] = None) -> Path:
    """Return project root or exit with error if not found."""
    root = find_project_root(start)
    if not root:
        error("Not a Gate19 project (no pyproject.toml or gate19.toml found). Run `gate19 new` or `gate19 init`.")
        raise typer.Exit(1)
    return root

def ensure_python_version(version: str) -> str:
    """Validate python version string."""
    import re
    if not re.match(r"^3\.\d+(\.\d+)?$", version.strip()):
        error(f"Invalid Python version: {version}")
        raise typer.Exit(1)
    return version.strip()
