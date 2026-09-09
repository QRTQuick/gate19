"""pyproject.toml helpers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore

try:
    import tomli_w  # type: ignore

    HAS_TOMLI_W = True
except ImportError:
    HAS_TOMLI_W = False


def load_pyproject(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def dump_toml(data: dict) -> str:
    """Minimal TOML dumper if tomli_w unavailable."""
    if HAS_TOMLI_W:
        return tomli_w.dumps(data)  # type: ignore
    # Fallback very simple
    import json

    # naive fallback - use manual formatting
    # We'll implement a simple recursive dumper for our use case
    lines: list[str] = []

    def format_value(v):
        if isinstance(v, str):
            return f'"{v}"'
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, list):
            inner = ", ".join(format_value(x) for x in v)
            return f"[{inner}]"
        if isinstance(v, dict):
            inner = ", ".join(f"{k} = {format_value(val)}" for k, val in v.items())
            return f"{{{inner}}}"
        return f'"{str(v)}"'

    def recurse(d: dict, prefix: str = ""):
        # separate plain values and tables
        plain = {k: v for k, v in d.items() if not isinstance(v, dict)}
        tables = {k: v for k, v in d.items() if isinstance(v, dict)}
        for k, v in plain.items():
            lines.append(f"{k} = {format_value(v)}")
        for k, v in tables.items():
            # check if all values are non-dict -> inline?
            # For pyproject we need tables
            full = f"{prefix}.{k}" if prefix else k
            # if table contains only plain values, emit [table]
            if all(not isinstance(val, dict) for val in v.values()):
                lines.append("")
                lines.append(f"[{full}]")
                for tk, tv in v.items():
                    lines.append(f"{tk} = {format_value(tv)}")
            else:
                recurse(v, full)

    recurse(data)
    return "\n".join(lines) + "\n"


def update_dependencies(pyproject_path: Path, packages: list[str], remove: bool = False) -> None:
    """Add or remove dependencies in pyproject.toml [project].dependencies."""
    data = load_pyproject(pyproject_path)
    if "project" not in data:
        data["project"] = {}
    if "dependencies" not in data["project"]:
        data["project"]["dependencies"] = []
    deps: list[str] = list(data["project"]["dependencies"])

    # Normalize for comparison: package name lower before extras/version
    def name_of(dep: str) -> str:
        # strip version specifiers, extras
        m = re.split(r"[<>=!~\[]", dep.strip(), maxsplit=1)
        return m[0].strip().lower()

    if remove:
        names_to_remove = {name_of(p) for p in packages}
        deps = [d for d in deps if name_of(d) not in names_to_remove]
    else:
        existing_names = {name_of(d) for d in deps}
        for pkg in packages:
            n = name_of(pkg)
            if n not in existing_names:
                deps.append(pkg)
            else:
                # update version if provided
                for i, d in enumerate(deps):
                    if name_of(d) == n:
                        # only update if pkg has version specifier
                        if any(c in pkg for c in "<>=!~"):
                            deps[i] = pkg
                        break
    data["project"]["dependencies"] = deps
    # write back preserving original formatting roughly
    content = dump_toml(data)
    pyproject_path.write_text(content, encoding="utf-8")


def update_requirements_txt(project_root: Path, packages: list[str] | None = None, remove: bool = False) -> None:
    req_path = project_root / "requirements.txt"
    existing: list[str] = []
    if req_path.exists():
        existing = [l.strip() for l in req_path.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]

    def name_of(dep: str) -> str:
        m = re.split(r"[<>=!~\[]", dep.strip(), maxsplit=1)
        return m[0].strip().lower()

    if packages is None:
        # sync from pyproject
        pyproject = load_pyproject(project_root / "pyproject.toml")
        deps = pyproject.get("project", {}).get("dependencies", [])
        existing = deps
    else:
        if remove:
            names = {name_of(p) for p in packages}
            existing = [d for d in existing if name_of(d) not in names]
        else:
            existing_names = {name_of(d) for d in existing}
            for pkg in packages:
                if name_of(pkg) not in existing_names:
                    existing.append(pkg)
                else:
                    # update if versioned
                    if any(c in pkg for c in "<>=!~"):
                        for i, d in enumerate(existing):
                            if name_of(d) == name_of(pkg):
                                existing[i] = pkg
                                break
    req_path.write_text("\n".join(existing) + ("\n" if existing else ""), encoding="utf-8")
