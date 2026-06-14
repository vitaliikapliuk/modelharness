from cache import TTLCache


def test_fresh_value_is_returned():
    c = TTLCache(ttl_seconds=60)
    c.set("k", "v")
    assert c.get("k") == "v"
    assert c.size() == 1
