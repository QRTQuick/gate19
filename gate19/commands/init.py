"""gate19 init — initialize gate19 in existing project."""

from __future__ import annotations

from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.config.manager import write_default_config
from gate19.utils.console import console, success, info, warning
from gate19.utils.fs import ensure_dir, write_file
from gate19.utils.git import init_git
from gate19.utils.venv import create_venv

@app.command("init")
def init_command(
    template: str = typer.Option("app", "--template", "-t", help="Template to use"),
    python: str = typer.Option("3.11", "--python", "-p", help="Python version"),
    no_venv: bool = typer.Option(False, "--no-venv", help="Skip venv"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite config"),
):
    """Initialize Gate19 in current directory. 🔧"""
    cwd = Path.cwd()
    info(f"Initializing Gate19 in {cwd}")

    # pyproject.toml check
    if not (cwd / "pyproject.toml").exists() or force:
        from gate19.templates.definitions import get_template
        tmpl = get_template(template)
        deps = tmpl.dependencies + tmpl.dev_dependencies
        deps_str = ",\n    ".join(f'"{d}"' for d in deps) if deps else ""
        content = f'''[project]
name = "{cwd.name}"
version = "0.1.0"
description = "Gate19 {template} project"
readme = "README.md"
requires-python = ">={python}"
license = {{ text = "MIT" }}
dependencies = [
    {deps_str},
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
        write_file(cwd / "pyproject.toml", content)
        success("Created pyproject.toml")
    else:
        info("pyproject.toml already exists — skipping")

    if not (cwd / "gate19.toml").exists() or force:
        write_default_config(cwd, python=python, template=template)
        success("Created gate19.toml")
    else:
        info("gate19.toml already exists — skipping")

    for d in ["src", "tests", "docs", "assets"]:
        ensure_dir(cwd / d)

    if not (cwd / ".gitignore").exists():
        write_file(cwd / ".gitignore", "__pycache__/\n.venv/\ndist/\nbuild/\n*.egg-info/\n.pytest_cache/\n")
        success("Created .gitignore")
    if not (cwd / ".env").exists():
        write_file(cwd / ".env", f"PROJECT_NAME={cwd.name}\nTEMPLATE={template}\n")

    init_git(cwd)
    if not no_venv:
        create_venv(cwd)

    success(f"Initialized Gate19 project in {cwd} ✓")
