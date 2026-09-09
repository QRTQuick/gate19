"""gate19 cache — cache management."""

from __future__ import annotations

import typer
from rich.table import Table
from gate19.cli.app import cache_app
from gate19.cache.manager import CacheManager
from gate19.utils.console import console, success, info

@cache_app.command("info")
def cache_info():
    """Show cache info. ℹ️"""
    cm = CacheManager()
    data = cm.info()
    table = Table(title="Gate19 Cache", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Directory", data["cache_dir"])
    table.add_row("Files", str(data["count"]))
    table.add_row("Total Size", data["total_size_human"])
    table.add_row("Raw Bytes", str(data["total_size"]))
    console.print(table)

@cache_app.command("clear")
def cache_clear(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Clear all cache. 🧹"""
    if not yes:
        confirm = typer.confirm("Clear all Gate19 cache?")
        if not confirm:
            console.print("[dim]Cancelled[/]")
            raise typer.Exit(0)
    cm = CacheManager()
    count = cm.clear()
    success(f"Cleared {count} cache entries ✓")

@cache_app.command("prune")
def cache_prune(
    days: int = typer.Option(7, "--days", help="Prune entries older than N days"),
):
    """Prune old cache entries. ✂️"""
    cm = CacheManager()
    removed = cm.prune(max_age_seconds=days*24*3600)
    success(f"Pruned {removed} entries older than {days} days ✓")

# Also allow `gate19 cache` without subcommand to show info
@cache_app.callback(invoke_without_command=True)
def cache_callback(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        cache_info()
