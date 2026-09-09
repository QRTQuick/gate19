"""gate19 python — python version management."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import typer

from gate19.cli.app import python_app
from gate19.python.manager import PythonManager
from gate19.utils.console import console

@python_app.command("list")
def python_list():
    """List available and installed Python versions. 🐍"""
    mgr = PythonManager()
    mgr.show_table()

@python_app.command("install")
def python_install(
    version: str = typer.Argument(..., help="Python version to install (e.g. 3.13, 3.12.5)"),
):
    """Install a Python version. 📥"""
    mgr = PythonManager()
    ok = mgr.install(version)
    if not ok:
        raise typer.Exit(1)

@python_app.command("use")
def python_use(
    version: str = typer.Argument(..., help="Python version to use"),
    project: Optional[Path] = typer.Option(None, "--project", "-p", help="Project path (default: cwd)"),
):
    """Switch project to use a Python version. 🔄"""
    mgr = PythonManager()
    root = project or Path.cwd()
    ok = mgr.use(version, project_root=root)
    if not ok:
        raise typer.Exit(1)

@python_app.command("remove")
def python_remove(
    version: str = typer.Argument(..., help="Python version to remove"),
):
    """Remove an installed Python version. 🗑️"""
    mgr = PythonManager()
    # Also support `gate19 python remove` without arg? spec says no arg
    ok = mgr.remove(version)
    if not ok:
        raise typer.Exit(1)

# Alias for `uninstall`
@python_app.command("uninstall")
def python_uninstall(
    version: str = typer.Argument(..., help="Python version to remove"),
):
    """Alias for remove."""
    mgr = PythonManager()
    ok = mgr.remove(version)
    if not ok:
        raise typer.Exit(1)
