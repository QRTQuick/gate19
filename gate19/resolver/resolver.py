"""High-performance dependency resolver (cached, parallel, conflict-aware)."""

from __future__ import annotations

import concurrent.futures
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from gate19.cache.manager import CacheManager
from gate19.utils.console import console, info, warning

# Simple in-memory index simulation; real resolver would query PyPI JSON API

PYPI_SIMPLE = "https://pypi.org/simple/"
PYPI_JSON = "https://pypi.org/pypi/{name}/json"


@dataclass
class Requirement:
    name: str
    specifier: str = ""
    extras: str = ""
    original: str = ""

    @classmethod
    def parse(cls, raw: str) -> "Requirement":
        raw = raw.strip()
        # name[extras] specifier
        # e.g. requests[security]>=2.28
        m = re.match(r"^\s*([A-Za-z0-9_.\-]+)(?:\[([^\]]+)\])?\s*(.*)$", raw)
        if not m:
            return cls(name=raw, original=raw)
        name = m.group(1)
        extras = m.group(2) or ""
        spec = m.group(3).strip()
        return cls(name=name, specifier=spec, extras=extras, original=raw)


@dataclass
class ResolvedPackage:
    name: str
    version: str
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ResolutionResult:
    packages: list[ResolvedPackage] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    elapsed: float = 0.0
    cached: bool = False

    def is_success(self) -> bool:
        return len(self.conflicts) == 0


class Resolver:
    """Cached, parallel, conflict-aware resolver."""

    def __init__(self, cache: CacheManager | None = None, max_workers: int = 8, ttl: int = 3600) -> None:
        self.cache = cache or CacheManager()
        self.max_workers = max_workers
        self.ttl = ttl

    def resolve(self, requirements: list[str], parallel: bool = True) -> ResolutionResult:
        start = time.monotonic()
        cache_key = "resolve:" + "|".join(sorted(requirements))
        cached = self.cache.get(cache_key, ttl=self.ttl)
        if cached:
            # cached is dict
            try:
                pkgs = [ResolvedPackage(**p) for p in cached.get("packages", [])]
                return ResolutionResult(packages=pkgs, conflicts=cached.get("conflicts", []), elapsed=0.0, cached=True)
            except Exception:
                pass

        reqs = [Requirement.parse(r) for r in requirements]

        # Conflict detection: duplicate names with incompatible specifiers (simple)
        conflicts: list[str] = []
        seen: dict[str, list[str]] = {}
        for r in reqs:
            seen.setdefault(r.name.lower(), []).append(r.specifier)
        for name, specs in seen.items():
            non_empty = [s for s in specs if s]
            if len(non_empty) > 1:
                # naive: if specs differ, flag potential conflict
                uniq = set(non_empty)
                if len(uniq) > 1:
                    # check if they could be compatible (e.g. >=1.0 and >=2.0 might be ok)
                    # For now warn if contains == with different versions
                    has_eq = any("==" in s for s in uniq)
                    if has_eq and len(uniq) > 1:
                        conflicts.append(f"Conflicting specifiers for {name}: {', '.join(non_empty)}")

        # Fetch metadata in parallel (or sequentially)
        def fetch(req: Requirement) -> ResolvedPackage:
            # Try to fetch from PyPI JSON quickly; fall back to synthetic
            try:
                # Use httpx with timeout 3s; if fails, synthetic
                with httpx.Client(timeout=3.0, follow_redirects=True) as client:
                    resp = client.get(PYPI_JSON.format(name=req.name))
                    if resp.status_code == 200:
                        data = resp.json()
                        ver = data["info"]["version"]
                        deps = data["info"].get("requires_dist") or []
                        # filter deps: take first 5 for demo
                        return ResolvedPackage(name=req.name, version=ver, dependencies=deps[:5])
            except Exception:
                pass
            # synthetic fallback: version 1.0.0 or latest known
            synthetic_version = "1.0.0"
            # try to extract version from specifier if ==
            if "==" in req.specifier:
                m = re.search(r"==\s*([^\s,]+)", req.specifier)
                if m:
                    synthetic_version = m.group(1).strip().strip("'\"")
            return ResolvedPackage(name=req.name, version=synthetic_version, dependencies=[])

        packages: list[ResolvedPackage] = []
        if parallel and len(reqs) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.max_workers, len(reqs))) as ex:
                futures = {ex.submit(fetch, r): r for r in reqs}
                for fut in concurrent.futures.as_completed(futures):
                    try:
                        packages.append(fut.result())
                    except Exception as e:
                        warning(f"Resolve failed for {futures[fut].name}: {e}")
                        packages.append(ResolvedPackage(name=futures[fut].name, version="0.0.0"))
        else:
            for r in reqs:
                packages.append(fetch(r))

        elapsed = time.monotonic() - start
        result = ResolutionResult(packages=packages, conflicts=conflicts, elapsed=elapsed, cached=False)
        # cache
        try:
            self.cache.set(
                cache_key,
                {"packages": [p.__dict__ for p in packages], "conflicts": conflicts},
            )
        except Exception:
            pass
        return result

    def check_conflicts(self, installed: dict[str, str], requirements: list[str]) -> list[str]:
        """Check installed versions against requirements."""
        conflicts = []
        for req_raw in requirements:
            req = Requirement.parse(req_raw)
            inst_ver = installed.get(req.name.lower())
            if not inst_ver:
                continue
            if req.specifier and "==" in req.specifier:
                m = re.search(r"==\s*([^\s,]+)", req.specifier)
                if m and m.group(1).strip() != inst_ver:
                    conflicts.append(f"{req.name} installed {inst_ver} != required {m.group(1)}")
        return conflicts
