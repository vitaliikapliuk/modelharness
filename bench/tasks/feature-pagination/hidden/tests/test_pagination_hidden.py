import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import pytest
from store import ItemStore
from pagination import paginate


def make_store(n=10):
    return ItemStore([{"id": i, "v": f"item{i}"} for i in range(n, 0, -1)])  # reversed insertion


def test_orders_by_id_and_paginates_without_overlap():
    store = make_store(7)
    page1 = paginate(store, None, 3)
    page2 = paginate(store, page1["next_cursor"], 3)
    page3 = paginate(store, page2["next_cursor"], 3)
    ids = [i["id"] for i in page1["items"] + page2["items"] + page3["items"]]
    assert ids == [1, 2, 3, 4, 5, 6, 7]
    assert page3["next_cursor"] is None


def test_stable_under_appends():
    items = [{"id": i} for i in range(1, 6)]
    store = ItemStore(items)
    page1 = paginate(store, None, 2)
    store._items.append({"id": 100})
    page2 = paginate(store, page1["next_cursor"], 2)
    assert [i["id"] for i in page2["items"]] == [3, 4]


def test_limit_validation():
    store = make_store(3)
    with pytest.raises(ValueError):
        paginate(store, None, 0)
    with pytest.raises(ValueError):
        paginate(store, None, 101)


def test_corrupt_cursor_raises():
    store = make_store(3)
    with pytest.raises(ValueError):
        paginate(store, "not-a-real-cursor!!!", 2)
