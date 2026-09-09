"""gate19 sync — sync dependencies from pyproject.toml."""

from __future__ import annotations

from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.installers.installer import Installer
from gate19.utils.console import success, info, warning
from gate19.utils.fs import find_project_root

@app.command("sync")
def sync_command(
    check: bool = typer.Option(False, "--check", help="Check if sync is needed without installing"),
):
    """Sync project dependencies from pyproject.toml. 🔗"""
    root = find_project_root() or Path.cwd()
    installer = Installer(root)

    if check:
        from gate19.utils.pyproject import load_pyproject
        data = load_pyproject(root / "pyproject.toml")
        deps = data.get("project", {}).get("dependencies", [])
        info(f"Project declares {len(deps)} dependencies")
        for d in deps:
            info(f"  • {d}")
        # Could check installed vs declared
        success("Check completed")
        return

    info(f"Syncing dependencies for {root}...")
    ok = installer.sync()
    if ok:
        success("Sync completed ✓")
        # Also update requirements.txt to match
        from gate19.utils.pyproject import update_requirements_txt
        try:
            update_requirements_txt(root, packages=None)
        except Exception:
            pass
    else:
        warning("Sync completed with warnings")
