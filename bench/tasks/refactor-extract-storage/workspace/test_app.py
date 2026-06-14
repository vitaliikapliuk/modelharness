import app


def setup_function(_):
    app.reset()


def test_add_and_list():
    a = app.add_order("alice", 10.555)
    b = app.add_order("alice", 5)
    app.add_order("bob", 99)
    assert [o["id"] for o in app.orders_for("alice")] == [a, b]
    assert app.orders_for("alice")[0]["amount"] == 10.55


def test_total_formatting():
    app.add_order("alice", 10)
    app.add_order("alice", 2.5)
    assert app.user_total("alice") == "alice: $12.50"


def test_validation():
    import pytest
    with pytest.raises(ValueError):
        app.add_order("", 5)
    with pytest.raises(ValueError):
        app.add_order("alice", 0)
