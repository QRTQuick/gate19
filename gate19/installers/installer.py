"""Pip-based installer abstraction with caching, progress, and parallel support."""

from __future__ import annotations

import concurrent.futures
import subprocess
import sys
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from gate19.cache.manager import CacheManager
from gate19.resolver.resolver import Resolver
from gate19.utils.console import console, info, warning, success, error
from gate19.utils.venv import venv_pip, venv_python


class Installer:
    def __init__(self, project_root: Path, cache: CacheManager | None = None) -> None:
        self.project_root = project_root
        self.cache = cache or CacheManager()
        self.resolver = Resolver(cache=self.cache)

    def _pip_exe(self) -> list[str]:
        pip = venv_pip(self.project_root)
        if pip.exists():
            return [str(pip)]
        return [sys.executable, "-m", "pip"]

    def install(self, packages: list[str], no_cache: bool = False, parallel: bool = True) -> bool:
        if not packages:
            warning("No packages to install")
            return False

        # Resolve first (cached, conflict-aware)
        info(f"Resolving {len(packages)} package(s)...")
        result = self.resolver.resolve(packages, parallel=parallel)
        if result.conflicts:
            for c in result.conflicts:
                warning(f"Conflict: {c}")
            # not fatal, continue

        if result.cached:
            console.print(f"[dim]  ↻ Resolved from cache in {result.elapsed:.2f}s[/]")
        else:
            console.print(f"[dim]  ✓ Resolved {len(result.packages)} packages in {result.elapsed:.2f}s[/]")

        # Install with pip
        pip = self._pip_exe()
        console.print(f"[cyan]  → Installing with pip: {' '.join(packages)}[/]")

        # Use progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Installing {', '.join(packages)}...", total=None)
            cmd = pip + ["install", *packages]
            # Use --quiet but capture
            try:
                result_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                # PEP 668 fallback for system pip
                if result_proc.returncode != 0 and "externally-managed-environment" in result_proc.stderr:
                    cmd.append("--break-system-packages")
                    result_proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                progress.update(task, completed=1)
                if result_proc.returncode != 0:
                    # Show error but not overly verbose
                    err = result_proc.stderr.strip()[:1000] or result_proc.stdout.strip()[:1000]
                    error(f"pip install failed:\n{err}")
                    return False
                success(f"Installed {', '.join(packages)}")
                if result_proc.stdout:
                    # optionally show pip output in dim
                    out = result_proc.stdout.strip().splitlines()[-5:]
                    for line in out:
                        if line.strip():
                            console.print(f"[dim]    {line.strip()}[/]")
                return True
            except subprocess.TimeoutExpired:
                error("pip install timed out after 300s")
                return False
            except Exception as e:
                error(f"Install failed: {e}")
                return False

    def uninstall(self, packages: list[str]) -> bool:
        pip = self._pip_exe()
        cmd = pip + ["uninstall", "-y", *packages]
        console.print(f"[cyan]  → Uninstalling: {' '.join(packages)}[/]")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0 and "externally-managed-environment" in result.stderr:
                cmd.append("--break-system-packages")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                error(f"pip uninstall failed: {result.stderr.strip()[:800]}")
                return False
            success(f"Removed {', '.join(packages)}")
            return True
        except Exception as e:
            error(f"Uninstall failed: {e}")
            return False

    def freeze(self) -> str:
        pip = self._pip_exe()
        try:
            result = subprocess.run(pip + ["freeze"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
            return ""
        except Exception:
            return ""

    def sync(self) -> bool:
        """Sync from pyproject.toml dependencies."""
        from gate19.utils.pyproject import load_pyproject

        pyproj = self.project_root / "pyproject.toml"
        data = load_pyproject(pyproj)
        deps = data.get("project", {}).get("dependencies", [])
        if not deps:
            warning("No dependencies in pyproject.toml")
            return False
        return self.install(deps)

    def update_all(self, packages: list[str] | None = None) -> bool:
        pip = self._pip_exe()
        if packages:
            cmd = pip + ["install", "--upgrade", *packages]
        else:
            # upgrade all: pip freeze + upgrade
            freeze = self.freeze()
            if not freeze.strip():
                warning("Nothing installed to update")
                return False
            pkgs = [line.split("==")[0].split(">=")[0].strip() for line in freeze.splitlines() if line.strip()]
            cmd = pip + ["install", "--upgrade", *pkgs]
        console.print(f"[cyan]  → Updating: {' '.join(cmd[2:])}[/]")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0 and "externally-managed-environment" in result.stderr:
                cmd.append("--break-system-packages")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                error(f"Update failed: {result.stderr.strip()[:800]}")
                return False
            success("Update completed")
            return True
        except Exception as e:
            error(f"Update failed: {e}")
            return False
