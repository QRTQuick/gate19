"""gate19 lint — linter."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.utils.console import console, success, info, warning
from gate19.utils.fs import find_project_root

@app.command("lint")
def lint_command(
    path: Path | None = typer.Argument(None, help="Path to lint"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix where possible"),
):
    """Lint code with ruff & mypy. 🔍"""
    root = find_project_root() or Path.cwd()
    target = path or root
    info(f"Linting {target}...")

    ran = False
    # ruff check
    try:
        probe = subprocess.run([sys.executable, "-m", "ruff", "--help"], capture_output=True, text=True, timeout=5)
        if probe.returncode == 0:
            cmd = [sys.executable, "-m", "ruff", "check", str(target)]
            if fix:
                cmd.append("--fix")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            console.print(result.stdout[:2000] if result.stdout else "[green]  ✓ ruff: no issues[/]")
            if result.stderr:
                console.print(f"[dim]{result.stderr[:500]}[/]")
            ran = True
        else:
            if "No module named" in (probe.stderr or "") or "No module named" in (probe.stdout or ""):
                console.print("[dim]  ○ ruff not installed — skipping[/]")
            else:
                console.print("[dim]  ○ ruff not installed — skipping[/]")
    except Exception as e:
        warning(f"ruff error: {e}")

    # mypy
    try:
        probe = subprocess.run([sys.executable, "-m", "mypy", "--help"], capture_output=True, text=True, timeout=5)
        if probe.returncode == 0:
            result = subprocess.run([sys.executable, "-m", "mypy", str(target)], capture_output=True, text=True, timeout=60)
            if result.stdout.strip():
                console.print(result.stdout[:3000])
            else:
                console.print("[green]  ✓ mypy: no issues[/]")
            ran = True
        else:
            console.print("[dim]  ○ mypy not installed — skipping[/]")
    except Exception as e:
        warning(f"mypy error: {e}")

    # Fallback: py_compile check
    if not ran:
        info("Running fallback syntax check...")
        errors = []
        for py in target.rglob("*.py"):
            if ".venv" in py.parts or "__pycache__" in py.parts:
                continue
            try:
                compile(py.read_text(encoding="utf-8"), str(py), "exec")
            except SyntaxError as e:
                errors.append(f"{py}: {e}")
        if errors:
            for e in errors[:20]:
                console.print(f"[red]  ✗ {e}[/]")
            warning(f"Found {len(errors)} syntax errors")
        else:
            success("Lint passed (syntax check) ✓")
    else:
        success("Lint completed ✓")
