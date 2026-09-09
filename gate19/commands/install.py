"""gate19 install — install packages."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import typer
from gate19.cli.app import app
from gate19.installers.installer import Installer
from gate19.utils.console import console, success, info, warning, error
from gate19.utils.fs import find_project_root
from gate19.utils.pyproject import update_dependencies, update_requirements_txt

@app.command("install")
def install_command(
    packages: Optional[List[str]] = typer.Argument(None, help="Packages to install (e.g. requests, 'fastapi>=0.110')"),
    dev: bool = typer.Option(False, "--dev", "-D", help="Install as dev dependency"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable cache"),
    upgrade: bool = typer.Option(False, "--upgrade", "-U", help="Upgrade packages"),
):
    """Install packages. 📦"""
    root = find_project_root() or Path.cwd()
    installer = Installer(root)

    if not packages:
        # No args: sync from pyproject
        info("No packages specified — syncing from pyproject.toml...")
        ok = installer.sync()
        if ok:
            success("Synced dependencies ✓")
        else:
            warning("Sync completed with warnings")
        return

    # Normalize - allow comma separated?
    pkgs = []
    for p in packages:
        pkgs.extend([x.strip() for x in p.split(",") if x.strip()])

    info(f"Installing {len(pkgs)} package(s) into {root}...")

    # Update pyproject before or after? Do after successful install, but also before to track
    ok = installer.install(pkgs, no_cache=no_cache)
    if ok:
        # Update project files
        try:
            pyproj = root / "pyproject.toml"
            if pyproj.exists():
                update_dependencies(pyproj, pkgs, remove=False)
            update_requirements_txt(root, pkgs, remove=False)
            success(f"Added {', '.join(pkgs)} to project dependencies ✓")
        except Exception as e:
            warning(f"Failed to update pyproject.toml: {e}")
    else:
        error("Install failed")
        raise typer.Exit(1)
