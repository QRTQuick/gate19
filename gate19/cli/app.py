"""Main Typer CLI app — Gate19."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from gate19 import __version__
from gate19.utils.console import console, banner

# Create the main Typer app
app = typer.Typer(
    name="gate19",
    help="Gate19 — The Next Generation Python Project Manager ⚡",
    add_completion=True,
    pretty_exceptions_show_locals=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)

# Sub-app for python management
python_app = typer.Typer(
    name="python",
    help="Manage Python versions [dim](list, install, use, remove)[/]",
    rich_markup_mode="rich",
)
app.add_typer(python_app, name="python")

# Sub-app for cache management
cache_app = typer.Typer(
    name="cache",
    help="Manage Gate19 cache [dim](info, clear, prune)[/]",
    rich_markup_mode="rich",
)
app.add_typer(cache_app, name="cache")


def _version_callback(value: bool):
    if value:
        console.print(f"[bold magenta]gate19[/] version [cyan]{__version__}[/]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-V", help="Show version and exit", callback=_version_callback, is_eager=True
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Gate19 — Fast, smart, and developer-friendly Python project manager."""
    if ctx.invoked_subcommand is None:
        # No subcommand: show help + banner
        banner()
        console.print(f"[dim]gate19 v{__version__} — type [cyan]gate19 --help[/] for commands[/]\n")
        # Show quick help
        ctx.obj = {"verbose": verbose}
        # Let typer show help
        # Instead of exiting, print help
        # Use get_help via click
        try:
            # typer's app will handle help if we call with --help?
            # Just print available commands table
            table = Table(title="Available Commands", show_header=True, header_style="bold magenta")
            table.add_column("Command", style="cyan", no_wrap=True)
            table.add_column("Description", style="white")
            table.add_row("new", "Create a new project")
            table.add_row("init", "Initialize gate19 in existing project")
            table.add_row("install", "Install packages")
            table.add_row("remove", "Remove packages")
            table.add_row("update", "Update packages")
            table.add_row("sync", "Sync dependencies from pyproject.toml")
            table.add_row("freeze", "Show frozen dependencies")
            table.add_row("clean", "Clean project artifacts & caches")
            table.add_row("doctor", "Diagnose project health")
            table.add_row("format", "Format code (black + isort)")
            table.add_row("lint", "Lint code (ruff + mypy)")
            table.add_row("test", "Run tests (pytest)")
            table.add_row("benchmark", "Run benchmarks")
            table.add_row("check", "Check dependency health")
            table.add_row("audit", "Security audit")
            table.add_row("build", "Build wheel & sdist")
            table.add_row("publish", "Publish to PyPI")
            table.add_row("python", "Manage Python versions")
            table.add_row("cache", "Manage cache")
            table.add_row("run", "Run command in project venv")
            console.print(table)
            console.print("\n[dim]Examples:[/]")
            console.print("  [cyan]gate19 new myapp --template fastapi[/]")
            console.print("  [cyan]gate19 install requests[/]")
            console.print("  [cyan]gate19 python list[/]")
            console.print("  [cyan]gate19 build[/]")
        except Exception:
            pass


# Import commands to register them
# We do this after app definition to avoid circular imports
from gate19.commands import (
    new,  # noqa: F401,E402
    install,  # noqa: F401,E402
    remove,  # noqa: F401,E402
    update,  # noqa: F401,E402
    sync,  # noqa: F401,E402
    freeze,  # noqa: F401,E402
    clean,  # noqa: F401,E402
    doctor,  # noqa: F401,E402
    format as format_cmd,  # noqa: F401,E402
    lint,  # noqa: F401,E402
    test_cmd,  # noqa: F401,E402
    benchmark,  # noqa: F401,E402
    build,  # noqa: F401,E402
    publish,  # noqa: F401,E402
    python_mgmt,  # noqa: F401,E402
    cache as cache_cmd,  # noqa: F401,E402
    check,  # noqa: F401,E402
    security,  # noqa: F401,E402
    run,  # noqa: F401,E402
    init as init_cmd,  # noqa: F401,E402
)

if __name__ == "__main__":
    app()
