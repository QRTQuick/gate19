"""gate19 test — run pytest."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import typer
from gate19.cli.app import app
from gate19.utils.console import console, info, warning, success
from gate19.utils.fs import find_project_root

@app.command("test")
def test_command(
    args: Optional[List[str]] = typer.Argument(None, help="Extra args passed to pytest"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Run with coverage"),
):
    """Run tests with pytest. 🧪"""
    root = find_project_root() or Path.cwd()
    info(f"Running tests in {root}...")

    cmd = [sys.executable, "-m", "pytest"]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov", ".", "--cov-report", "term-missing"])

    if args:
        cmd.extend(args)
    # default: discover tests
    # Ensure path exists
    # if no args and no tests dir, just run pytest

    # First check if pytest is available
    probe = subprocess.run([sys.executable, "-m", "pytest", "--version"], capture_output=True, text=True, timeout=5)
    if probe.returncode != 0 and "No module named" in (probe.stderr or probe.stdout or ""):
        warning("pytest not installed — falling back to unittest")
        fallback = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=str(root))
        if fallback.returncode == 0:
            success("Tests passed (unittest) ✓")
        else:
            # If unittest also fails because no tests, consider success
            if fallback.returncode != 0:
                # check if tests exist
                has_tests = any((root / "tests").rglob("test_*.py"))
                if not has_tests and not (root / "tests").exists():
                    success("No tests found — nothing to run ✓")
                    return
            raise typer.Exit(fallback.returncode)
        return

    try:
        result = subprocess.run(cmd, cwd=str(root))
        if result.returncode == 0:
            success("Tests passed ✓")
        else:
            # If tests failed due to import errors etc, try unittest as fallback when pytest not properly installed?
            warning(f"Tests failed with code {result.returncode}")
            raise typer.Exit(result.returncode)
    except FileNotFoundError:
        warning("pytest not installed — install with `gate19 install pytest`")
        fallback = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=str(root))
        if fallback.returncode == 0:
            success("unittest fallback passed")
        else:
            raise typer.Exit(fallback.returncode)
