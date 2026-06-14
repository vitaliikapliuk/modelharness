import handlers


def test_happy_paths():
    assert handlers.get_profile("u1") == {"status": 200, "data": {"name": "Alice"}}
    assert handlers.get_greeting("u1") == {"status": 200, "data": "Hello, Alice!"}
    assert handlers.get_name_length("u1") == {"status": 200, "data": 5}


def test_error_paths_identical_across_handlers():
    for fn in (handlers.get_profile, handlers.get_greeting, handlers.get_name_length):
        assert fn("") == {"error": "invalid id", "status": 400}
        assert fn("nope") == {"error": "not found", "status": 404}
        assert fn("u2") == {"error": "inactive", "status": 403}
        assert fn(123) == {"error": "invalid id", "status": 400}
