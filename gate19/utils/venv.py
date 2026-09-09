"""Virtual environment helpers."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from gate19.utils.console import console, info, warning

VENV_NAME = ".venv"


def venv_path(project_root: Path) -> Path:
    return project_root / VENV_NAME


def venv_python(project_root: Path) -> Path:
    vp = venv_path(project_root)
    if sys.platform == "win32":
        return vp / "Scripts" / "python.exe"
    return vp / "bin" / "python"


def venv_pip(project_root: Path) -> Path:
    vp = venv_path(project_root)
    if sys.platform == "win32":
        return vp / "Scripts" / "pip.exe"
    return vp / "bin" / "pip"


def create_venv(project_root: Path, python: str | None = None) -> bool:
    """Create .venv in project_root. Returns True if created."""
    venv_dir = venv_path(project_root)
    if venv_dir.exists():
        return False
    # Choose python executable
    py_exe = python or sys.executable
    # Try to find requested version if not sys.executable
    # Fallback to sys.executable
    if python and python != sys.executable:
        # try `pythonX.Y` on PATH
        import shutil

        found = shutil.which(f"python{python}") or shutil.which(f"python{python.split('.')[0]}") or shutil.which(python)
        if found:
            py_exe = found

    info(f"Creating virtual environment at [bold]{venv_dir}[/] using [cyan]{py_exe}[/]")
    try:
        # Use venv module
        result = subprocess.run(
            [py_exe, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            warning(f"venv creation failed: {result.stderr.strip()[:500]}")
            # Fallback: try with sys.executable
            if py_exe != sys.executable:
                result2 = subprocess.run(
                    [sys.executable, "-m", "venv", str(venv_dir)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result2.returncode == 0:
                    console.print("[green]  ✓ Virtual environment created[/]")
                    return True
                warning(f"Fallback also failed: {result2.stderr.strip()[:500]}")
            return False
        console.print("[green]  ✓ Virtual environment created[/]")
        return True
    except Exception as e:
        warning(f"Failed to create venv: {e}")
        return False


def run_in_venv(project_root: Path, args: list[str], **kwargs) -> subprocess.CompletedProcess:
    py = venv_python(project_root)
    if not py.exists():
        py = Path(sys.executable)
    # If first arg is python-like, replace
    # else run via venv python -m pip etc.
    return subprocess.run(args, **kwargs)


def pip_install(project_root: Path, packages: list[str], extra_args: list[str] | None = None) -> int:
    """Install packages into project venv or global if no venv."""
    pip = venv_pip(project_root)
    if not pip.exists():
        pip_exe = [sys.executable, "-m", "pip"]
    else:
        pip_exe = [str(pip)]
    cmd = pip_exe + ["install", *packages]
    if extra_args:
        cmd.extend(extra_args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode
