import asyncio

from runner import run_all


def test_run_all_processes_in_order():
    out = asyncio.run(run_all([{"id": 1}, {"id": 2}]))
    assert [r["id"] for r in out] == [1, 2]
    assert all(r["processed"] for r in out)
    assert out[0]["length"] == len("data-1")
