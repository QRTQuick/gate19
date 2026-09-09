"""Cache tests."""

import time
from pathlib import Path
import tempfile
from gate19.cache.manager import CacheManager

def test_cache_set_get():
    tmp = Path(tempfile.mkdtemp())
    cm = CacheManager(cache_dir=tmp)
    cm.set("foo", {"a": 1})
    assert cm.get("foo") == {"a": 1}

def test_cache_ttl():
    tmp = Path(tempfile.mkdtemp())
    cm = CacheManager(cache_dir=tmp)
    cm.set("bar", "value")
    assert cm.get("bar", ttl=3600) == "value"
    # with ttl 0, should still return if not expired? we set ttl very small and sleep
    time.sleep(0.1)
    assert cm.get("bar", ttl=0) is None  # ttl 0 means immediately expired? depends on implementation: age > ttl
    # Actually if ttl 0, age 0.1 >0 => expired => None

def test_cache_clear():
    tmp = Path(tempfile.mkdtemp())
    cm = CacheManager(cache_dir=tmp)
    cm.set("k1", "v1")
    cm.set("k2", "v2")
    info = cm.info()
    assert info["count"] >= 2
    cm.clear()
    assert cm.info()["count"] == 0

def test_cache_prune():
    tmp = Path(tempfile.mkdtemp())
    cm = CacheManager(cache_dir=tmp)
    cm.set("old", "val")
    # prune with max_age 0 should remove
    removed = cm.prune(max_age_seconds=0)
    assert removed >= 1

def test_cache_info_structure():
    tmp = Path(tempfile.mkdtemp())
    cm = CacheManager(cache_dir=tmp)
    info = cm.info()
    assert "cache_dir" in info
    assert "count" in info
    assert "total_size" in info
