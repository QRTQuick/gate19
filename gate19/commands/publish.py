"""gate19 publish — publish to PyPI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.utils.console import console, success, info, warning, error
from gate19.utils.fs import find_project_root

@app.command("publish")
def publish_command(
    repository: str = typer.Option("pypi", "--repository", "-r", help="Repository (pypi, testpypi)"),
    token: str | None = typer.Option(None, "--token", help="PyPI token (or set TWINE_PASSWORD)"),
    username: str | None = typer.Option(None, "--username", "-u", help="Username (default: __token__)"),
    skip_build: bool = typer.Option(False, "--skip-build", help="Skip building before publish"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Check without uploading"),
):
    """Publish package to PyPI. 🚀"""
    root = find_project_root() or Path.cwd()
    dist = root / "dist"

    if not skip_build and not dry_run:
        if not dist.exists() or not any(dist.iterdir()):
            info("No dist artifacts found — building...")
            from gate19.commands.build import build_command
            # Call build via subprocess to avoid recursion
            result = subprocess.run([sys.executable, "-m", "build"], cwd=str(root))
            if result.returncode != 0:
                error("Build failed — aborting publish")
                raise typer.Exit(1)

    if not dist.exists() or not any(dist.iterdir()):
        error(f"No files in {dist} — run `gate19 build` first")
        raise typer.Exit(1)

    files = list(dist.glob("*"))
    info(f"Publishing {len(files)} file(s) to {repository}...")
    for f in files:
        console.print(f"  • {f.name}")

    if dry_run:
        console.print("[yellow]Dry run — not uploading[/]")
        # Validate with twine check if available
        try:
            result = subprocess.run([sys.executable, "-m", "twine", "check", *[str(f) for f in files]], capture_output=True, text=True, timeout=30)
            console.print(result.stdout[:2000] if result.stdout else "")
            if result.returncode == 0:
                success("Twine check passed ✓")
            else:
                warning(f"Twine check warnings:\n{result.stdout[:1000]}\n{result.stderr[:500]}")
        except Exception:
            info("Install twine for validation: pip install twine")
        success("Dry run completed ✓")
        return

    # Ensure twine
    try:
        probe = subprocess.run([sys.executable, "-m", "twine", "--help"], capture_output=True, timeout=5)
        has_twine = probe.returncode == 0
    except Exception:
        has_twine = False

    if not has_twine:
        warning("twine not installed — installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "twine"], capture_output=True)
        probe = subprocess.run([sys.executable, "-m", "twine", "--help"], capture_output=True, timeout=5)
        has_twine = probe.returncode == 0
        if not has_twine:
            error("Failed to install twine")
            raise typer.Exit(1)

    cmd = [sys.executable, "-m", "twine", "upload"]
    if repository != "pypi":
        cmd.extend(["--repository", repository])
    if token:
        # Use token as password with username __token__
        cmd.extend(["--username", username or "__token__", "--password", token])
    elif username:
        cmd.extend(["--username", username])
    cmd.extend([str(f) for f in files])

    console.print(f"[cyan]  → Uploading...[/]")
    # Don't print token
    safe_cmd = [c if c != token else "***" for c in cmd]
    console.print(f"[dim]{' '.join(safe_cmd)}[/]")

    result = subprocess.run(cmd, cwd=str(root))
    if result.returncode == 0:
        success(f"Published to {repository} ✓")
    else:
        error(f"Publish failed with code {result.returncode}")
        raise typer.Exit(result.returncode)
