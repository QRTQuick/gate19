"""gate19 run — run command in project venv."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import typer
from gate19.cli.app import app
from gate19.utils.console import console, info, error
from gate19.utils.fs import find_project_root
from gate19.utils.venv import venv_python

@app.command("run", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run_command(
    ctx: typer.Context,
    command: Optional[List[str]] = typer.Argument(None, help="Command to run (e.g. main.py or 'python -c \"print(1)\"')"),
):
    """Run a command inside the project venv. ▶️"""
    root = find_project_root() or Path.cwd()
    venv_py = venv_python(root)
    python_exe = str(venv_py) if venv_py.exists() else sys.executable

    # Typer captures; need to handle extra args
    # If command is None, try to get from ctx.args
    args = list(command or [])
    # Also include unknown extra args
    if ctx.args:
        args.extend(ctx.args)
    # Also handle case where user does `gate19 run -- python -c "..."`
    # typer will put "--" handling; ctx.args will contain rest

    if not args:
        error("No command provided. Usage: gate19 run <command>")
        console.print("[dim]Examples:[/]")
        console.print("  gate19 run main.py")
        console.print("  gate19 run -- python -c \"print(1)\"")
        console.print("  gate19 run -- pytest -v")
        raise typer.Exit(1)

    # If single arg is a .py file, run with python
    if len(args) == 1 and args[0].endswith(".py"):
        cmd = [python_exe, args[0]]
    elif args[0] in ("python", "python3", "py"):
        cmd = [python_exe, *args[1:]]
    else:
        # Try if first arg is a file
        first_path = root / args[0]
        if first_path.exists() and first_path.suffix == ".py":
            cmd = [python_exe, str(first_path), *args[1:]]
        else:
            # Check if command exists on PATH or needs python -m
            # For generic commands, run directly but with venv PATH prepend
            cmd = args
            # If cmd[0] is not found, try python -m
            import shutil
            if not shutil.which(cmd[0]):
                # maybe it's a module? try python -m
                cmd = [python_exe, "-m", *args]
            else:
                # Prepend venv bin to PATH for subprocess
                pass

    info(f"Running: {' '.join(cmd)} (venv: {python_exe})")
    # Prepare env with venv bin in PATH
    import os
    env = os.environ.copy()
    venv_bin = venv_py.parent if venv_py.exists() else Path(python_exe).parent
    env["PATH"] = str(venv_bin) + os.pathsep + env.get("PATH", "")
    env["VIRTUAL_ENV"] = str(venv_py.parent.parent) if venv_py.exists() else env.get("VIRTUAL_ENV", "")

    try:
        result = subprocess.run(cmd, cwd=str(root), env=env)
        raise typer.Exit(result.returncode)
    except FileNotFoundError as e:
        error(f"Command not found: {e}")
        raise typer.Exit(1)
