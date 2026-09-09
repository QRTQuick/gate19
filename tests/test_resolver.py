"""Resolver tests."""

from gate19.resolver.resolver import Resolver, Requirement
from gate19.cache.manager import CacheManager
import tempfile
from pathlib import Path

def test_requirement_parse():
    r = Requirement.parse("requests>=2.28")
    assert r.name == "requests"
    assert "2.28" in r.specifier
    r2 = Requirement.parse("fastapi[standard]>=0.110")
    assert r2.name == "fastapi"
    assert r2.extras == "standard"

def test_resolver_basic():
    cm = CacheManager(cache_dir=Path(tempfile.mkdtemp()))
    res = Resolver(cache=cm, ttl=10)
    result = res.resolve(["requests>=2.0", "rich"], parallel=False)
    assert len(result.packages) == 2
    names = {p.name for p in result.packages}
    assert "requests" in names
    assert "rich" in names
    assert result.elapsed >= 0

def test_resolver_conflict_detection():
    cm = CacheManager(cache_dir=Path(tempfile.mkdtemp()))
    res = Resolver(cache=cm)
    result = res.resolve(["requests==2.28", "requests==2.31"], parallel=False)
    # should detect conflict
    assert len(result.conflicts) >= 1

def test_resolver_cache():
    tmp = Path(tempfile.mkdtemp())
    cm = CacheManager(cache_dir=tmp)
    res = Resolver(cache=cm, ttl=3600)
    r1 = res.resolve(["rich"], parallel=False)
    assert not r1.cached
    r2 = res.resolve(["rich"], parallel=False)
    assert r2.cached

def test_resolver_parallel():
    cm = CacheManager(cache_dir=Path(tempfile.mkdtemp()))
    res = Resolver(cache=cm)
    result = res.resolve(["requests", "rich", "click"], parallel=True)
    assert len(result.packages) == 3
