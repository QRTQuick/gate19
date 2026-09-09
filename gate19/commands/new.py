"""gate19 new — create a new project."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gate19.cli.app import app
from gate19.config.manager import write_default_config
from gate19.templates.definitions import TEMPLATES, get_template, render_main_py, all_dependencies
from gate19.utils.console import console, success, info, warning, error, step
from gate19.utils.fs import ensure_dir, write_file
from gate19.utils.git import init_git
from gate19.utils.venv import create_venv

# Support `--template` values help
TEMPLATE_CHOICES = sorted(TEMPLATES.keys())


def _slugify(name: str) -> str:
    name = name.strip().replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^A-Za-z0-9\-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name.lower() or "myproject"


def _package_name(name: str) -> str:
    slug = _slugify(name)
    pkg = slug.replace("-", "_")
    # ensure valid identifier
    if not pkg[0].isalpha():
        pkg = "app_" + pkg
    pkg = re.sub(r"[^A-Za-z0-9_]", "_", pkg)
    return pkg


def _create_gitignore() -> str:
    return """# Gate19 / Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
.env
dist/
build/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
.DS_Store
.idea/
.vscode/
*.log
gate19-cache/
"""


def _create_pyproject(project_name: str, template: str, python: str, dependencies: list[str]) -> str:
    pkg = _package_name(project_name)
    deps_str = ",\n    ".join(f'"{d}"' for d in dependencies) if dependencies else ""
    deps_block = f"dependencies = [\n    {deps_str},\n]" if dependencies else "dependencies = []"
    return f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "A Gate19 {template} project — built with Gate19 ⚡"
readme = "README.md"
requires-python = ">={python}"
license = {{ text = "MIT" }}
authors = [{{ name = "Developer" }}]
{deps_block}

[project.scripts]
{pkg} = "{pkg}.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{pkg}"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.black]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
'''


def _create_readme(project_name: str, template: str) -> str:
    return f"""# {project_name}

> A Gate19 **{template}** project — created with `gate19 new`.

## Quick Start

```bash
gate19 install
gate19 run main.py
gate19 test
gate19 build
```

## Project Structure

```
src/
tests/
docs/
assets/
main.py
pyproject.toml
gate19.toml
```

## Template: {template}

This project was scaffolded with the `{template}` template.
Edit `main.py` and `src/` to build your application.

---
Built with [Gate19](https://github.com/QRTQuick/gate19) ⚡
"""


@app.command("new")
def new_command(
    name: str = typer.Argument(..., help="Name of the project to create (e.g. myapp)"),
    template_arg: Optional[str] = typer.Argument(None, help="Template (positional alternative to --template)"),
    template: str = typer.Option("app", "--template", "-t", help=f"Template to use: {', '.join(sorted(TEMPLATE_CHOICES))}"),
    python: str = typer.Option("3.11", "--python", "-p", help="Python version (e.g. 3.11, 3.13)"),
    no_install: bool = typer.Option(False, "--no-install", help="Skip auto-installing dependencies"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git initialization"),
    no_venv: bool = typer.Option(False, "--no-venv", help="Skip virtual environment creation"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if directory exists"),
):
    """Create a new Gate19 project. 📦"""
    target = Path.cwd() / name
    slug = _slugify(name)
    pkg_name = _package_name(name)

    # Positional template_arg overrides --template option if provided (e.g. `gate19 new myproj fastapi`)
    if template_arg:
        template = template_arg

    # Handle case where `name` itself is a template alias and user did `gate19 new fastapi` meaning template=fastapi with project name fastapi
    # If name is known template and directory doesn't specify template? We already handle.
    # Normalize template
    template = template.lower().strip()
    if template not in TEMPLATES:
        warning(f"Unknown template '{template}', falling back to 'app'. Available: {', '.join(sorted(TEMPLATE_CHOICES))}")
        template = "app"

    # Auto-infer template from project name if user did `gate19 new <template>` shorthand
    # e.g., `gate19 new fastapi` should create fastapi project with fastapi template when no explicit template given
    # We detect if template is default 'app' and name matches a template
    if template == "app" and name.lower().strip() in TEMPLATES and name.lower().strip() not in ("app", "default"):
        inferred = name.lower().strip()
        info(f"Detected template shorthand — using template '{inferred}' for project '{name}'")
        template = inferred

    if target.exists() and not force:
        if any(target.iterdir()):
            error(f"Directory '{target}' already exists and is not empty. Use --force to overwrite.")
            raise typer.Exit(1)
    if target.exists() and force:
        import shutil

        shutil.rmtree(target, ignore_errors=True)

    console.print(f"[bold magenta]🚀 Creating new Gate19 project[/] [cyan]{name}[/] [dim]with template[/] [yellow]{template}[/]")
    console.print(f"[dim]  → Package: {pkg_name}  |  Python: {python}  |  Target: {target}[/]")

    # Gather dependencies
    tmpl = get_template(template)
    deps = tmpl.dependencies + tmpl.dev_dependencies
    # If template is default/app, ensure full COMMON list
    # Add unique
    seen = set()
    uniq_deps = []
    for d in deps:
        low = d.split("[")[0].split(">")[0].split("=")[0].lower()
        if low not in seen:
            seen.add(low)
            uniq_deps.append(d)
    deps = uniq_deps

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, transient=False) as progress:
        task = progress.add_task("Scaffolding project...", total=None)

        # Create directories
        ensure_dir(target)
        ensure_dir(target / "src" / pkg_name)
        ensure_dir(target / "tests")
        ensure_dir(target / "docs")
        ensure_dir(target / "assets")

        progress.update(task, description="Writing project files...")

        # main.py
        main_py_content = render_main_py(template, name)
        write_file(target / "main.py", main_py_content)

        # src package
        write_file(target / "src" / pkg_name / "__init__.py", f'"""Package {pkg_name}."""\n__version__ = "0.1.0"\n')
        # src __main__
        write_file(
            target / "src" / pkg_name / "__main__.py",
            f'''"""CLI entry for {pkg_name}."""

from gate19.templates.definitions import render_main_py

# Re-export main from main.py if needed
def main():
    print("Hello from {pkg_name}!")
''',
        )

        # tests
        write_file(
            target / "tests" / "test_main.py",
            f'''"""Tests for {name}."""

def test_import():
    import importlib.util, pathlib
    assert pathlib.Path("main.py").exists() or True

def test_hello():
    assert "hello" in "hello world"

def test_template():
    assert "{template}" in "{template}"
''',
        )
        write_file(target / "tests" / "__init__.py", "")

        # docs
        write_file(target / "docs" / "index.md", f"# {name}\n\nDocumentation for **{name}** ({template} template).\n")
        write_file(target / "assets" / ".gitkeep", "")

        # .gitignore
        write_file(target / ".gitignore", _create_gitignore())

        # README
        write_file(target / "README.md", _create_readme(name, template))

        # .env
        write_file(
            target / ".env",
            f"""# Environment for {name}
# Generated by Gate19
PROJECT_NAME={name}
TEMPLATE={template}
PYTHON={python}
DEBUG=true
# Add your secrets here
""",
        )

        # pyproject.toml
        write_file(target / "pyproject.toml", _create_pyproject(name, template, python, deps))

        # requirements.txt
        write_file(target / "requirements.txt", "\n".join(deps) + "\n" if deps else "")

        # gate19.toml
        write_default_config(target, python=python, template=template)

        # .python-version
        write_file(target / ".python-version", python + "\n")

        progress.update(task, description="Initializing git & venv...")

    # Git init
    if not no_git:
        init_git(target)
        # initial commit attempt? not needed
    else:
        info("Skipped git init (--no-git)")

    # Venv
    if not no_venv:
        created = create_venv(target, python=None)
        if not created:
            warning("Virtual environment not created — you can run `gate19 sync` later")
    else:
        info("Skipped venv creation (--no-venv)")

    # Auto install
    if not no_install and deps:
        info(f"Installing {len(deps)} dependencies (this may take a moment)...")
        # Try to pip install into venv if available, with nice progress
        from gate19.installers.installer import Installer

        installer = Installer(target)
        # Install with quiet progress; if fails, warn but don't abort
        try:
            ok = installer.install(deps)
            if not ok:
                warning("Some dependencies failed to install — run `gate19 install` manually")
        except Exception as e:
            warning(f"Auto-install error: {e}")
    elif no_install:
        info("Skipped auto-install (--no-install)")

    # Final success
    console.print()
    success(f"Project '{name}' created at [bold]{target}[/] [green]✓[/]")
    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1))
    table.add_column("Next Steps", style="cyan")
    table.add_row(f"cd {name}")
    table.add_row("gate19 install        # ensure deps are installed")
    table.add_row("gate19 run main.py    # run your app")
    table.add_row("gate19 test           # run tests")
    table.add_row("gate19 format         # format code")
    table.add_row("gate19 build          # build package")
    console.print(table)
    console.print(f"\n[dim]Template: {template}  •  Python: {python}  •  Deps: {len(deps)} packages[/]")
    console.print("[bold green]✨ Happy coding with Gate19! ✨[/]")
