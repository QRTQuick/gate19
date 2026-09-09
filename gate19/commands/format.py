"""gate19 format — formatter."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import typer
from gate19.cli.app import app
from gate19.utils.console import console, success, info, warning, error
from gate19.utils.fs import find_project_root


@app.command("format")
def format_command(
    path: Path | None = typer.Argument(None, help="Path to format (default: project root)"),
    check: bool = typer.Option(False, "--check", help="Check only, don't write"),
):
    """Format code with black & isort. ✨"""
    root = find_project_root() or Path.cwd()
    target = path or root
    info(f"Formatting {target}...")

    # Try black
    ran_any = False
    for tool, cmd_base in [
        ("black", [sys.executable, "-m", "black"]),
        ("isort", [sys.executable, "-m", "isort"]),
        ("ruff", [sys.executable, "-m", "ruff", "format"]),
    ]:
        try:
            # Check if tool available
            probe = subprocess.run(cmd_base + ["--help"], capture_output=True, text=True, timeout=5)
            if probe.returncode != 0 and "No module named" in (probe.stderr or ""):
                console.print(f"[dim]  ○ {tool} not installed — skipping[/]")
                continue
            # Also skip if help not found (module missing returns 1 with stderr)
            if probe.returncode != 0 and probe.stderr and "No module named" in probe.stderr:
                console.print(f"[dim]  ○ {tool} not installed — skipping[/]")
                continue
            if probe.returncode != 0 and "No module named" in (probe.stdout or ""):
                console.print(f"[dim]  ○ {tool} not installed — skipping[/]")
                continue
            cmd = cmd_base + ([str(target)] if tool != "ruff" else [str(target)])
            if check:
                cmd += ["--check"] if tool in ("black", "isort") else ["--check"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                console.print(f"[green]  ✓ {tool} passed[/]")
                if result.stdout.strip():
                    console.print(f"[dim]{result.stdout.strip()[:500]}[/]")
            else:
                # black check returns 1 if would reformat
                if check:
                    console.print(f"[yellow]  ⚠ {tool} would reformat[/]")
                    if result.stdout:
                        console.print(result.stdout[:500])
                else:
                    console.print(f"[yellow]  ⚠ {tool}: {result.stderr.strip()[:300] or result.stdout.strip()[:300]}[/]")
            ran_any = True
        except FileNotFoundError:
            console.print(f"[dim]  ○ {tool} not found[/]")
        except Exception as e:
            warning(f"{tool} error: {e}")

    if not ran_any:
        # Fallback: simple trailing whitespace fix
        warning("No formatters found — doing minimal cleanup...")
        count = 0
        for py in target.rglob("*.py"):
            if ".venv" in py.parts or "__pycache__" in py.parts:
                continue
            try:
                text = py.read_text(encoding="utf-8")
                lines = [l.rstrip() for l in text.splitlines()]
                new = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
                if new != text and not check:
                    py.write_text(new, encoding="utf-8")
                    count += 1
            except Exception:
                pass
        if count:
            success(f"Cleaned trailing whitespace in {count} files")
        else:
            info("No formatting needed (fallback)")

    else:
        success("Format completed ✓")
