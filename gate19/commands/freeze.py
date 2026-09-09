"""gate19 freeze — show frozen dependencies."""

from __future__ import annotations

from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.installers.installer import Installer
from gate19.utils.console import console
from gate19.utils.fs import find_project_root

@app.command("freeze")
def freeze_command(
    output: Path | None = typer.Option(None, "--output", "-o", help="Write to file instead of stdout"),
):
    """Show frozen dependencies (pip freeze). ❄️"""
    root = find_project_root() or Path.cwd()
    installer = Installer(root)
    frozen = installer.freeze()
    if not frozen.strip():
        # fallback: show pyproject deps
        from gate19.utils.pyproject import load_pyproject
        data = load_pyproject(root / "pyproject.toml")
        deps = data.get("project", {}).get("dependencies", [])
        frozen = "\n".join(deps) + ("\n" if deps else "")
        if not frozen.strip():
            frozen = "# No dependencies found\n"

    if output:
        output.write_text(frozen, encoding="utf-8")
        console.print(f"[green]✓ Frozen dependencies written to {output}[/]")
    else:
        console.print(frozen, highlight=False)
