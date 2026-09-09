"""Cache manager — download & package caching."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any

from platformdirs import user_cache_dir

from gate19.utils.console import info, warning

DEFAULT_CACHE_DIR = Path(user_cache_dir("gate19"))


def get_cache_dir(custom: str | Path | None = None) -> Path:
    if custom:
        p = Path(custom).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p
    DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return DEFAULT_CACHE_DIR


class CacheManager:
    """Simple file-based cache with TTL and size tracking."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.cache_dir = get_cache_dir(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._meta_file = self.cache_dir / "cache_meta.json"
        self._meta: dict[str, Any] = self._load_meta()

    def _load_meta(self) -> dict[str, Any]:
        if self._meta_file.exists():
            try:
                return json.loads(self._meta_file.read_text())
            except Exception:
                return {}
        return {}

    def _save_meta(self) -> None:
        try:
            self._meta_file.write_text(json.dumps(self._meta, indent=2))
        except Exception:
            pass

    def _key_path(self, key: str) -> Path:
        h = hashlib.sha256(key.encode()).hexdigest()[:16]
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)[:40]
        return self.cache_dir / f"{safe}_{h}.cache"

    def get(self, key: str, ttl: int | None = None) -> Any | None:
        path = self._key_path(key)
        if not path.exists():
            return None
        if ttl is not None:
            age = time.time() - path.stat().st_mtime
            if age > ttl:
                return None
        try:
            text = path.read_text()
        except Exception:
            try:
                return path.read_bytes()
            except Exception:
                return None
        try:
            return json.loads(text)
        except Exception:
            # Not JSON -> return raw text (for plain string values)
            return text

    def set(self, key: str, value: Any) -> None:
        path = self._key_path(key)
        try:
            if isinstance(value, (dict, list)):
                path.write_text(json.dumps(value))
            elif isinstance(value, str):
                path.write_text(value)
            elif isinstance(value, bytes):
                path.write_bytes(value)
            else:
                path.write_text(json.dumps(value, default=str))
            self._meta[key] = {"path": str(path), "time": time.time()}
            self._save_meta()
        except Exception as e:
            warning(f"Cache set failed for {key}: {e}")

    def clear(self) -> int:
        count = 0
        for p in self.cache_dir.glob("*.cache"):
            try:
                p.unlink()
                count += 1
            except Exception:
                pass
        self._meta.clear()
        self._save_meta()
        return count

    def prune(self, max_age_seconds: int = 3600 * 24 * 7) -> int:
        """Remove entries older than max_age."""
        now = time.time()
        removed = 0
        for p in self.cache_dir.glob("*.cache"):
            try:
                age = now - p.stat().st_mtime
                if age > max_age_seconds:
                    p.unlink()
                    removed += 1
            except Exception:
                pass
        return removed

    def info(self) -> dict[str, Any]:
        total_size = 0
        count = 0
        for p in self.cache_dir.glob("*.cache"):
            try:
                total_size += p.stat().st_size
                count += 1
            except Exception:
                pass
        return {
            "cache_dir": str(self.cache_dir),
            "count": count,
            "total_size": total_size,
            "total_size_human": _human_size(total_size),
        }


def _human_size(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"
