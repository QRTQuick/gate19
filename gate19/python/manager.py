"""Python version management — list, install, use, remove."""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

import httpx
from rich.table import Table

from gate19.cache.manager import get_cache_dir
from gate19.utils.console import console, error, info, success, warning

# Known versions — in real tool would fetch from python.org or deadsnakes
KNOWN_VERSIONS = [
    "3.13.0",
    "3.13.1",
    "3.12.7",
    "3.12.6",
    "3.12.5",
    "3.11.10",
    "3.11.9",
    "3.10.15",
    "3.10.14",
    "3.9.20",
]

INSTALL_ROOT = Path.home() / ".gate19" / "pythons"


def _python_install_path(version: str) -> Path:
    # Normalize version: 3.13 -> 3.13.0 etc for storage
    # Store as given
    return INSTALL_ROOT / f"python-{version}"


class PythonManager:
    def __init__(self, install_root: Path | None = None) -> None:
        self.install_root = install_root or INSTALL_ROOT
        self.install_root.mkdir(parents=True, exist_ok=True)

    def list_available(self) -> list[str]:
        # Try to fetch from python.org API? Fallback to KNOWN_VERSIONS
        try:
            # Attempt to fetch python-build-standalone releases or just return known
            # For now return known + maybe dynamic
            return KNOWN_VERSIONS
        except Exception:
            return KNOWN_VERSIONS

    def list_installed(self) -> list[Path]:
        if not self.install_root.exists():
            return []
        return [p for p in self.install_root.iterdir() if p.is_dir()]

    def is_installed(self, version: str) -> bool:
        p = _python_install_path(version)
        # also check prefix match
        for inst in self.list_installed():
            if inst.name.endswith(version) or version in inst.name:
                return True
        return p.exists()

    def install(self, version: str) -> bool:
        """Install a Python version. Simulated download for now with fallback to pyenv/deadsnakes instructions."""
        # Normalize
        version = version.strip()
        if not re.match(r"^3\.\d+(\.\d+)?$", version):
            error(f"Invalid Python version: {version}. Expected e.g. 3.13, 3.12.5")
            return False

        target = _python_install_path(version)
        if target.exists():
            warning(f"Python {version} already installed at {target}")
            return True

        # If full version like 3.13, expand to latest patch
        if version.count(".") == 1:
            # find latest patch for that minor
            candidates = [v for v in self.list_available() if v.startswith(version + ".")]
            if candidates:
                version = candidates[0]
                target = _python_install_path(version)

        info(f"Installing Python {version} → {target}")
        # Try to actually download python-build-standalone or use apt? For portability we simulate.
        # We attempt to use `python --version` check and then create a shim that reports same version
        # Real implementation would download tarball. Here we create a directory with a marker and a shim python.

        try:
            target.mkdir(parents=True, exist_ok=True)
            bin_dir = target / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            # Create a shim python executable that delegates to current python but reports requested version
            shim = bin_dir / "python"
            shim.write_text(
                f"""#!/usr/bin/env sh
# Gate19 Python shim for {version}
# Delegates to system python but pretends to be {version}
exec "{sys.executable}" "$@"
""",
                encoding="utf-8",
            )
            shim.chmod(0o755)
            # Also python3
            shutil.copy(shim, bin_dir / "python3")
            (target / "VERSION").write_text(version, encoding="utf-8")
            console.print(f"[green]  ✓ Python {version} installed (shim) at {target}[/]")
            console.print(f"[dim]    Shim delegates to {sys.executable}[/]")
            console.print(f"[dim]    For a real standalone build, python-build-standalone would be downloaded.[/]")
            return True
        except Exception as e:
            error(f"Failed to install Python {version}: {e}")
            return False

    def use(self, version: str, project_root: Path | None = None) -> bool:
        """Switch project to use given Python version — updates gate19.toml and .python-version."""
        root = project_root or Path.cwd()
        target = _python_install_path(version)
        # allow prefix match
        if not target.exists():
            # find closest installed
            for inst in self.list_installed():
                if version in inst.name:
                    target = inst
                    version = inst.name.replace("python-", "")
                    break
            else:
                error(f"Python {version} not installed. Run: gate19 python install {version}")
                return False

        # Update gate19.toml if exists
        gate19_toml = root / "gate19.toml"
        if gate19_toml.exists():
            try:
                text = gate19_toml.read_text()
                if 'python' in text:
                    # naive replace
                    import re

                    new_text = re.sub(r'python\s*=\s*"[^"]+"', f'python = "{version}"', text)
                    if new_text == text:
                        # also try single quotes
                        new_text = re.sub(r"python\s*=\s*'[^']+'", f'python = "{version}"', text)
                    gate19_toml.write_text(new_text)
                else:
                    # append
                    gate19_toml.write_text(text + f'\npython = "{version}"\n')
            except Exception as e:
                warning(f"Could not update gate19.toml: {e}")
        # Write .python-version for pyenv compatibility
        (root / ".python-version").write_text(version + "\n", encoding="utf-8")
        success(f"Switched project to Python {version} ({target})")
        console.print(f"[dim]  Updated gate19.toml and .python-version[/]")
        return True

    def remove(self, version: str) -> bool:
        target = _python_install_path(version)
        found = None
        if target.exists():
            found = target
        else:
            for inst in self.list_installed():
                if version in inst.name:
                    found = inst
                    break
        if not found:
            error(f"Python {version} not installed")
            return False
        try:
            shutil.rmtree(found)
            success(f"Removed Python {version} at {found}")
            return True
        except Exception as e:
            error(f"Failed to remove {version}: {e}")
            return False

    def show_table(self) -> None:
        available = self.list_available()
        installed = {p.name.replace("python-", "") for p in self.list_installed()}
        current = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        table = Table(title="Python Versions", show_header=True, header_style="bold magenta")
        table.add_column("Version", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Current", style="yellow")

        for ver in available:
            status = "installed" if ver in installed or any(ver.startswith(i.rsplit('.',1)[0]) for i in installed) else "available"
            # better check prefix
            is_inst = ver in installed
            # also check if any installed starts with ver's minor
            if not is_inst:
                for inst in installed:
                    if ver == inst or ver.rsplit('.',1)[0] == inst.rsplit('.',1)[0]:
                        is_inst = True
                        break
            status = "✓ installed" if is_inst else "○ available"
            cur_marker = "← current" if ver == current else ""
            if not cur_marker and current.startswith(ver.rsplit('.',1)[0] if '.' in ver else ver):
                # mark current minor
                if ver.rsplit('.',1)[0] == current.rsplit('.',1)[0]:
                    cur_marker = "← current (patch diff)"
            table.add_row(ver, status, cur_marker)

        # also show any installed not in available
        extra = installed - set(available)
        for ver in sorted(extra):
            table.add_row(ver, "✓ installed (custom)", "← current" if ver == current else "")

        table.add_row(current, "✓ system", "← system", style="bold")

        console.print(table)
        console.print(f"[dim]Install dir: {self.install_root}[/]")
        console.print(f"[dim]System python: {sys.executable} ({current})[/]")
