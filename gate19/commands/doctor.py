"""gate19 doctor — diagnose project health."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.table import Table

from gate19 import __version__
from gate19.cli.app import app
from gate19.utils.console import console, success, warning, info, error
from gate19.utils.fs import find_project_root

CHECKS = []

def _check(label: str):
    def decorator(fn):
        CHECKS.append((label, fn))
        return fn
    return decorator


@app.command("doctor")
def doctor_command(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues automatically"),
):
    """Diagnose project health. 🩺"""
    console.print("[bold magenta]🩺 Gate19 Doctor[/]\n")

    root = find_project_root() or Path.cwd()
    info(f"Project root: {root}")
    info(f"Gate19 version: {__version__}")
    info(f"Python: {sys.version.split()[0]} @ {sys.executable}")
    info(f"Platform: {platform.system()} {platform.release()} ({platform.machine()})")
    console.print()

    issues = []
    passed = []

    # Check 1: pyproject.toml exists
    pyproj = root / "pyproject.toml"
    if pyproj.exists():
        passed.append("pyproject.toml exists ✓")
        console.print("[green]  ✓ pyproject.toml exists[/]")
    else:
        issues.append("pyproject.toml missing")
        console.print("[red]  ✗ pyproject.toml missing[/]")

    # Check 2: gate19.toml
    if (root / "gate19.toml").exists():
        passed.append("gate19.toml exists ✓")
        console.print("[green]  ✓ gate19.toml exists[/]")
    else:
        issues.append("gate19.toml missing (optional)")
        console.print("[yellow]  ⚠ gate19.toml missing (optional)[/]")

    # Check 3: .venv
    venv_path = root / ".venv"
    if venv_path.exists():
        py = venv_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        if py.exists():
            passed.append(".venv exists ✓")
            console.print("[green]  ✓ .venv exists[/]")
        else:
            issues.append(".venv corrupted (no python)")
            console.print("[yellow]  ⚠ .venv exists but python missing[/]")
            if fix:
                shutil.rmtree(venv_path, ignore_errors=True)
                from gate19.utils.venv import create_venv
                create_venv(root)
    else:
        issues.append(".venv missing")
        console.print("[yellow]  ⚠ .venv missing — run `gate19 sync`[/]")
        if fix:
            from gate19.utils.venv import create_venv
            create_venv(root)

    # Check 4: git
    if (root / ".git").exists():
        passed.append("git repo initialized ✓")
        console.print("[green]  ✓ git repo initialized[/]")
    else:
        issues.append("git not initialized")
        console.print("[yellow]  ⚠ git not initialized[/]")
        if fix:
            from gate19.utils.git import init_git
            init_git(root)

    # Check 5: dependencies installed?
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            passed.append("pip check passed ✓")
            console.print("[green]  ✓ pip check: no conflicts[/]")
        else:
            out = result.stdout.strip() + result.stderr.strip()
            if out:
                issues.append(f"pip check: {out[:200]}")
                console.print(f"[yellow]  ⚠ pip check: {out[:300]}[/]")
            else:
                console.print("[green]  ✓ pip check passed[/]")
    except Exception as e:
        warning(f"pip check failed: {e}")

    # Check 6: required tools
    tools = ["black", "ruff", "mypy", "pytest", "build", "twine"]
    for tool in tools:
        found = shutil.which(tool) is not None
        if found:
            console.print(f"[green]  ✓ {tool} available[/]")
        else:
            console.print(f"[dim]  ○ {tool} not found (optional)[/]")

    # Check 7: .gitignore
    if (root / ".gitignore").exists():
        console.print("[green]  ✓ .gitignore exists[/]")
    else:
        console.print("[yellow]  ⚠ .gitignore missing[/]")

    # Check 8: main.py or src
    if (root / "main.py").exists() or (root / "src").exists():
        console.print("[green]  ✓ Project scaffolding present[/]")
    else:
        console.print("[yellow]  ⚠ main.py / src missing[/]")

    console.print()
    # Summary table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Status", style="cyan")
    table.add_column("Count", style="white")
    table.add_row("Passed", str(len(passed)))
    table.add_row("Issues", str(len(issues)) if issues else "0 (healthy)")
    console.print(table)

    if not issues:
        success("\n✓ All checks passed — project is healthy! ✨")
    else:
        warning(f"\nFound {len(issues)} issue(s):")
        for iss in issues:
            console.print(f"  • {iss}")
        if not fix:
            console.print("\n[dim]Run with --fix to auto-fix where possible[/]")

    # Cache info
    from gate19.cache.manager import CacheManager
    cm = CacheManager()
    info_c = cm.info()
    console.print(f"\n[dim]Cache: {info_c['count']} files, {info_c['total_size_human']} at {info_c['cache_dir']}[/]")
