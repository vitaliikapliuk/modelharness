import sys, pathlib, asyncio, inspect, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import fetcher, processor, runner


def test_all_functions_are_coroutines():
    assert inspect.iscoroutinefunction(fetcher.fetch)
    assert inspect.iscoroutinefunction(processor.process)
    assert inspect.iscoroutinefunction(runner.run_all)


def test_behavior_preserved():
    out = asyncio.run(runner.run_all([{"id": 1}, {"id": 2}]))
    assert [r["id"] for r in out] == [1, 2]
    assert all(r["processed"] for r in out)
    assert out[0]["length"] == len("data-1")


def test_run_all_is_concurrent():
    sources = [{"id": i, "delay": 0.2} for i in range(5)]
    start = time.monotonic()
    out = asyncio.run(runner.run_all(sources))
    elapsed = time.monotonic() - start
    assert len(out) == 5
    assert elapsed < 0.6, f"5 x 0.2s sequential would be >=1.0s; got {elapsed:.2f}s"


def test_visible_tests_were_migrated_not_deleted():
    src = (pathlib.Path(__file__).resolve().parents[2] / "test_sync.py").read_text()
    assert "run_all" in src and "asyncio" in src


def test_sleep_is_native_asyncio():
    src = (pathlib.Path(__file__).resolve().parents[2] / "fetcher.py").read_text()
    assert "asyncio.sleep(" in src, "fetch must await asyncio.sleep per SPEC"
    assert "time.sleep" not in src, "time.sleep must be fully replaced"
    assert "to_thread" not in src, "thread-pool wrapping is not a migration"
