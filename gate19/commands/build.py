"""gate19 build — build wheel & sdist."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.utils.console import console, success, info, warning, error
from gate19.utils.fs import find_project_root

@app.command("build")
def build_command(
    wheel: bool = typer.Option(False, "--wheel", help="Build wheel only"),
    sdist: bool = typer.Option(False, "--sdist", help="Build sdist only"),
    outdir: Path | None = typer.Option(None, "--outdir", "-o", help="Output directory (default: dist)"),
):
    """Build wheel and source distribution. 🏗️"""
    root = find_project_root() or Path.cwd()
    info(f"Building project at {root}...")

    # Ensure build is available
    try:
        probe = subprocess.run([sys.executable, "-m", "build", "--help"], capture_output=True, text=True, timeout=5)
        has_build = probe.returncode == 0
    except Exception:
        has_build = False

    if not has_build:
        warning("`build` not installed — installing...")
        # Try normal pip, then with --break-system-packages for PEP 668
        install_cmd = [sys.executable, "-m", "pip", "install", "build"]
        result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0 and "externally-managed-environment" in result.stderr:
            install_cmd.append("--break-system-packages")
            subprocess.run(install_cmd, capture_output=True, text=True, timeout=60)
        # recheck
        probe = subprocess.run([sys.executable, "-m", "build", "--help"], capture_output=True, text=True, timeout=5)
        has_build = probe.returncode == 0

    if not has_build:
        error("Failed to install `build` package. Install manually: pip install build")
        raise typer.Exit(1)

    cmd = [sys.executable, "-m", "build"]
    if wheel and not sdist:
        cmd.append("--wheel")
    elif sdist and not wheel:
        cmd.append("--sdist")
    if outdir:
        cmd.extend(["--outdir", str(outdir)])
        out = outdir
    else:
        out = root / "dist"

    console.print(f"[cyan]  → Running: {' '.join(cmd)}[/]")
    result = subprocess.run(cmd, cwd=str(root))
    if result.returncode == 0:
        # list dist
        if out.exists():
            files = list(out.iterdir())
            success(f"Build succeeded — {len(files)} artifact(s) in {out} ✓")
            for f in files:
                console.print(f"  • {f.name} ({f.stat().st_size/1024:.1f} KB)")
        else:
            success("Build succeeded ✓")
    else:
        error(f"Build failed with code {result.returncode}")
        raise typer.Exit(result.returncode)
