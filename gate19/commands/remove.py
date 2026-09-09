"""gate19 remove — remove packages."""

from __future__ import annotations

from pathlib import Path
from typing import List
import typer
from gate19.cli.app import app
from gate19.installers.installer import Installer
from gate19.utils.console import success, info, warning, error
from gate19.utils.fs import find_project_root
from gate19.utils.pyproject import update_dependencies, update_requirements_txt


@app.command("remove")
def remove_command(
    packages: List[str] = typer.Argument(..., help="Packages to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation"),
):
    """Remove packages. 🗑️"""
    root = find_project_root() or Path.cwd()
    installer = Installer(root)

    pkgs = []
    for p in packages:
        pkgs.extend([x.strip() for x in p.split(",") if x.strip()])

    info(f"Removing {', '.join(pkgs)} from {root}...")

    ok = installer.uninstall(pkgs)
    if ok:
        try:
            pyproj = root / "pyproject.toml"
            if pyproj.exists():
                update_dependencies(pyproj, pkgs, remove=True)
            update_requirements_txt(root, pkgs, remove=True)
            success(f"Removed {', '.join(pkgs)} ✓")
        except Exception as e:
            warning(f"Failed to update pyproject.toml: {e}")
    else:
        error("Remove failed")
        raise typer.Exit(1)


# Alias `uninstall`
@app.command("uninstall")
def uninstall_alias(
    packages: List[str] = typer.Argument(..., help="Packages to remove"),
):
    """Alias for `remove`."""
    remove_command(packages)
