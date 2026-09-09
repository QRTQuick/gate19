"""gate19 check — dependency health checker."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.resolver.resolver import Resolver
from gate19.utils.console import console, success, info, warning, error
from gate19.utils.fs import find_project_root
from gate19.utils.pyproject import load_pyproject

@app.command("check")
def check_command():
    """Check dependency health & conflicts. 🔍"""
    root = find_project_root() or Path.cwd()
    info(f"Checking dependencies in {root}...")

    pyproj = root / "pyproject.toml"
    data = load_pyproject(pyproj)
    deps = data.get("project", {}).get("dependencies", [])
    if not deps:
        warning("No dependencies declared in pyproject.toml")
        # try requirements.txt
        req = root / "requirements.txt"
        if req.exists():
            deps = [l.strip() for l in req.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]
            info(f"Found {len(deps)} deps in requirements.txt")

    if not deps:
        console.print("[dim]No dependencies to check[/]")
        return

    console.print(f"[cyan]Checking {len(deps)} dependencies...[/]")
    resolver = Resolver()
    result = resolver.resolve(deps)
    if result.conflicts:
        error("Conflicts found:")
        for c in result.conflicts:
            console.print(f"  [red]✗ {c}[/]")
    else:
        success("No resolver conflicts ✓")

    # pip check
    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, timeout=15)
        out = proc.stdout.strip()
        if proc.returncode == 0 and (not out or "No broken requirements" in out):
            success("pip check: no broken requirements ✓")
        elif out:
            if "No broken requirements" in out:
                success("pip check: no broken requirements ✓")
            else:
                warning(f"pip check:\n{out[:1000]}")
        else:
            success("pip check passed")
    except Exception as e:
        warning(f"pip check failed: {e}")

    # Outdated check via pip list --outdated (optional)
    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "list", "--outdated", "--format=columns"], capture_output=True, text=True, timeout=20)
        if proc.stdout.strip().splitlines()[2:]:
            lines = proc.stdout.strip().splitlines()[2:][:10]
            if lines:
                console.print("\n[yellow]Outdated packages:[/]")
                for line in lines:
                    console.print(f"  • {line}")
                if len(proc.stdout.strip().splitlines()) > 12:
                    console.print(f"  ... and {len(proc.stdout.strip().splitlines())-12} more")
        else:
            console.print("[green]  ✓ All packages up-to-date[/]")
    except Exception:
        pass

    success("Check completed ✓")
