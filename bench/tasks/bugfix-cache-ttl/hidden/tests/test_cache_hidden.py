import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import time
import cache as cache_mod
from cache import TTLCache


def test_expired_entry_returns_default(monkeypatch):
    t = [1000.0]
    monkeypatch.setattr(cache_mod.time, "monotonic", lambda: t[0])
    c = TTLCache(ttl_seconds=10)
    c.set("k", "v")
    t[0] += 10.01
    assert c.get("k", default="MISS") == "MISS"


def test_expired_entry_is_evicted(monkeypatch):
    t = [1000.0]
    monkeypatch.setattr(cache_mod.time, "monotonic", lambda: t[0])
    c = TTLCache(ttl_seconds=10)
    c.set("k", "v")
    t[0] += 11
    c.get("k")
    assert c.size() == 0


def test_fresh_entry_still_works(monkeypatch):
    t = [1000.0]
    monkeypatch.setattr(cache_mod.time, "monotonic", lambda: t[0])
    c = TTLCache(ttl_seconds=10)
    c.set("k", "v")
    t[0] += 5
    assert c.get("k") == "v"
    assert c.size() == 1
