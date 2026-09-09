"""gate19 update — update packages."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import typer
from gate19.cli.app import app
from gate19.installers.installer import Installer
from gate19.utils.console import success, info, warning
from gate19.utils.fs import find_project_root

@app.command("update")
def update_command(
    packages: Optional[List[str]] = typer.Argument(None, help="Packages to update (default: all)"),
):
    """Update packages. 🔄"""
    root = find_project_root() or Path.cwd()
    installer = Installer(root)
    if packages:
        pkgs = []
        for p in packages:
            pkgs.extend([x.strip() for x in p.split(",") if x.strip()])
        info(f"Updating {', '.join(pkgs)}...")
        ok = installer.update_all(pkgs)
    else:
        info("Updating all packages...")
        ok = installer.update_all(None)

    if ok:
        success("Update completed ✓")
    else:
        warning("Update completed with warnings")
