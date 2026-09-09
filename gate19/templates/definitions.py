"""Template definitions - dependencies and scaffolding."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

# Common dev dependencies included in most templates
COMMON_DEV = ["pytest>=8.0", "black>=24.0", "isort>=5.12", "ruff>=0.4.0", "mypy>=1.9"]
COMMON_BASE = ["rich>=13.0", "python-dotenv>=1.0", "pydantic>=2.5"]


@dataclass
class Template:
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)
    extra_files: Dict[str, str] = field(default_factory=dict)  # path -> content
    main_py: str = ""
    readme_extra: str = ""


def _main_app(name: str) -> str:
    slug = name.replace("-", "_")
    return f'''"""Main entry for {name} - app template."""

from rich.console import Console
from dotenv import load_dotenv

load_dotenv()
console = Console()

def main() -> None:
    console.print("[bold green]✨ Welcome to {name}! — Gate19 app template[/]")
    console.print("Edit [cyan]main.py[/] to get started.")
    console.print("Run [yellow]gate19 --help[/] for available commands.")

if __name__ == "__main__":
    main()
'''


def _main_api(name: str) -> str:
    return f'''"""FastAPI API template for {name}."""

from fastapi import FastAPI
from rich.console import Console

console = Console()
app = FastAPI(title="{name}", version="0.1.0")

@app.get("/")
def root():
    return {{"message": "Hello from {name}!", "status": "ok"}}

@app.get("/health")
def health():
    return {{"status": "healthy"}}

def main():
    import uvicorn
    console.print("[bold green]Starting API server...[/]")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
'''


def _main_flask(name: str) -> str:
    return f'''"""Flask template for {name}."""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(message="Hello from {name}!", status="ok")

@app.route("/health")
def health():
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
'''


def _main_fastapi(name: str) -> str:
    return _main_api(name)


def _main_django_placeholder(name: str) -> str:
    return f'''"""Django template placeholder for {name}."""

# Run: django-admin startproject {name.replace('-','_')} .
# Gate19 has set up the base structure; complete Django setup with:
#   python -m django --version
#   django-admin startproject config .

from rich.console import Console
console = Console()

def main():
    console.print("[bold green]Django project: {name}[/]")
    console.print("To initialize Django:")
    console.print("  [cyan]django-admin startproject config .[/]")
    console.print("  [cyan]python manage.py migrate[/]")
    console.print("  [cyan]python manage.py runserver[/]")

if __name__ == "__main__":
    main()
'''


def _main_pygame(name: str) -> str:
    return f'''"""Pygame template for {name}."""

import sys
from rich.console import Console

console = Console()

def main():
    try:
        import pygame
    except ImportError:
        console.print("[red]pygame not installed. Run: gate19 install pygame[/]")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("{name}")
    clock = pygame.time.Clock()
    console.print("[green]Pygame window opened — close window to exit.[/]")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 30))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    console.print("[green]Game closed.[/]")

if __name__ == "__main__":
    main()
'''


def _main_cli(name: str) -> str:
    return f'''"""CLI template for {name} — built with Typer & Rich."""

import typer
from rich.console import Console

app = typer.Typer(help="{name} — awesome CLI built with Gate19")
console = Console()

@app.command()
def hello(name: str = "World"):
    """Say hello."""
    console.print(f"[bold green]Hello {{name}}! 👋 from {name}[/]")

@app.command()
def version():
    """Show version."""
    console.print("[cyan]{name} v0.1.0[/]")

if __name__ == "__main__":
    app()
'''


def _main_ai(name: str) -> str:
    return f'''"""AI template for {name}."""

from rich.console import Console
from rich.table import Table
import os
from dotenv import load_dotenv

load_dotenv()
console = Console()

def main():
    console.print("[bold magenta]🤖 {name} — AI Project[/]")
    table = Table(title="AI Stack")
    table.add_column("Library", style="cyan")
    table.add_column("Purpose", style="green")
    table.add_row("numpy", "Numerical compute")
    table.add_row("pandas", "Data manipulation")
    table.add_row("scikit-learn", "ML models")
    table.add_row("openai", "LLM API")
    console.print(table)
    console.print("\\n[dim]Add your API keys to .env and start building![/]")

if __name__ == "__main__":
    main()
'''


def _main_desktop(name: str) -> str:
    return f'''"""Desktop template for {name} — Textual / Rich based."""

from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel.fit("[bold green]🖥️ {name} — Desktop App[/]", border_style="blue"))
    console.print("This template uses [cyan]textual[/] for TUI or integrate PySide6/customtkinter for GUI.")
    console.print("\\nTry:")
    console.print("  [yellow]pip install textual[/]")
    console.print("  [yellow]textual --help[/]")

if __name__ == "__main__":
    main()
'''


def _main_library(name: str) -> str:
    slug = name.replace("-", "_")
    return f'''"""Library template for {name}."""

def hello(name: str = "World") -> str:
    """Example function for the library."""
    return f"Hello {{name}} from {name}!"

__all__ = ["hello"]

if __name__ == "__main__":
    print(hello())
'''


def _main_default(name: str) -> str:
    return _main_app(name)


TEMPLATES: Dict[str, Template] = {
    "app": Template(
        name="app",
        description="General purpose app with rich, pydantic, and common tools",
        dependencies=[
            "requests>=2.31",
            "rich>=13.0",
            "click>=8.1",
            "typer>=0.12",
            "python-dotenv>=1.0",
            "pydantic>=2.5",
            "watchdog>=4.0",
        ],
        dev_dependencies=COMMON_DEV,
        main_py="app",  # placeholder marker
    ),
    "default": Template(
        name="default",
        description="Default template — same as app",
        dependencies=[
            "requests>=2.31",
            "rich>=13.0",
            "click>=8.1",
            "typer>=0.12",
            "python-dotenv>=1.0",
            "pydantic>=2.5",
            "watchdog>=4.0",
        ],
        dev_dependencies=COMMON_DEV,
    ),
    "api": Template(
        name="api",
        description="API template with FastAPI and Uvicorn",
        dependencies=[
            "fastapi>=0.110",
            "uvicorn[standard]>=0.29",
            "pydantic>=2.5",
            "httpx>=0.27",
            "rich>=13.0",
            "python-dotenv>=1.0",
            "requests>=2.31",
        ],
        dev_dependencies=["pytest>=8.0", "pytest-asyncio>=0.23", "black>=24.0", "ruff>=0.4.0"],
    ),
    "flask": Template(
        name="flask",
        description="Flask web application",
        dependencies=[
            "flask>=3.0",
            "python-dotenv>=1.0",
            "rich>=13.0",
            "requests>=2.31",
            "pydantic>=2.5",
            "gunicorn>=22.0",
        ],
        dev_dependencies=COMMON_DEV,
    ),
    "fastapi": Template(
        name="fastapi",
        description="FastAPI production template",
        dependencies=[
            "fastapi>=0.110",
            "uvicorn[standard]>=0.29",
            "pydantic>=2.5",
            "rich>=13.0",
            "python-dotenv>=1.0",
            "httpx>=0.27",
            "pytest-asyncio>=0.23",
        ],
        dev_dependencies=COMMON_DEV,
    ),
    "django": Template(
        name="django",
        description="Django web framework",
        dependencies=[
            "django>=5.0",
            "djangorestframework>=3.15",
            "python-dotenv>=1.0",
            "rich>=13.0",
            "gunicorn>=22.0",
            "psycopg2-binary>=2.9",
        ],
        dev_dependencies=["pytest>=8.0", "pytest-django>=4.8", "black>=24.0", "ruff>=0.4.0", "mypy>=1.9"],
    ),
    "pygame": Template(
        name="pygame",
        description="Pygame game development",
        dependencies=[
            "pygame>=2.5",
            "rich>=13.0",
            "watchdog>=4.0",
            "pydantic>=2.5",
        ],
        dev_dependencies=["pytest>=8.0", "black>=24.0", "ruff>=0.4.0"],
    ),
    "cli": Template(
        name="cli",
        description="CLI application with Typer, Click, Rich, Prompt Toolkit",
        dependencies=[
            "typer>=0.12",
            "click>=8.1",
            "rich>=13.0",
            "prompt-toolkit>=3.0",
            "python-dotenv>=1.0",
            "pydantic>=2.5",
            "watchdog>=4.0",
        ],
        dev_dependencies=COMMON_DEV,
    ),
    "ai": Template(
        name="ai",
        description="AI / ML project with numpy, pandas, scikit-learn, openai",
        dependencies=[
            "numpy>=1.26",
            "pandas>=2.2",
            "scikit-learn>=1.4",
            "openai>=1.20",
            "pydantic>=2.5",
            "rich>=13.0",
            "python-dotenv>=1.0",
            "requests>=2.31",
            "tqdm>=4.66",
        ],
        dev_dependencies=COMMON_DEV,
    ),
    "desktop": Template(
        name="desktop",
        description="Desktop app with Textual / TUI",
        dependencies=[
            "textual>=0.60",
            "rich>=13.0",
            "watchdog>=4.0",
            "pydantic>=2.5",
            "python-dotenv>=1.0",
        ],
        dev_dependencies=COMMON_DEV,
    ),
    "library": Template(
        name="library",
        description="Python library — build, twine, and testing setup",
        dependencies=[
            "rich>=13.0",
            "typer>=0.12",
            "pydantic>=2.5",
        ],
        dev_dependencies=["build>=1.0", "twine>=5.0", "pytest>=8.0", "pytest-cov>=5.0", "black>=24.0", "isort>=5.12", "ruff>=0.4.0", "mypy>=1.9"],
    ),
}

# Ensure all templates have main_py factory
_MAIN_FACTORIES = {
    "app": _main_app,
    "default": _main_default,
    "api": _main_api,
    "flask": _main_flask,
    "fastapi": _main_fastapi,
    "django": _main_django_placeholder,
    "pygame": _main_pygame,
    "cli": _main_cli,
    "ai": _main_ai,
    "desktop": _main_desktop,
    "library": _main_library,
}

# Also support alias 'app' same as default
for _name, _tmpl in TEMPLATES.items():
    if not _tmpl.main_py or _tmpl.main_py in ("app",):
        # Will be generated dynamically per project name
        pass


def get_template(name: str) -> Template:
    key = name.lower().strip()
    if key not in TEMPLATES:
        # fallback to default
        key = "default"
    tmpl = TEMPLATES[key]
    return tmpl


def list_templates() -> list[str]:
    return sorted(k for k in TEMPLATES.keys() if k != "default")


def render_main_py(template_name: str, project_name: str) -> str:
    key = template_name.lower().strip()
    factory = _MAIN_FACTORIES.get(key, _main_default)
    return factory(project_name)


def all_dependencies(template_name: str) -> list[str]:
    tmpl = get_template(template_name)
    return tmpl.dependencies + tmpl.dev_dependencies
