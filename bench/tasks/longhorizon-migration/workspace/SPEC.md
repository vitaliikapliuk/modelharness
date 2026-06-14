# async migration spec

Migrate `fetcher.py`, `processor.py`, `runner.py` to asyncio:

1. `fetch(source: dict) -> dict` becomes `async def fetch`. Same logic; the
   `time.sleep(source.get("delay", 0))` call becomes `await asyncio.sleep(...)`.
2. `process(record: dict) -> dict` becomes `async def process`. Same logic.
3. `run_all(sources: list[dict]) -> list[dict]` becomes `async def run_all` and must
   execute fetch+process for all sources CONCURRENTLY (asyncio.gather or equivalent),
   preserving input order in the result list.
4. All public function names and signatures (besides async) stay the same.
5. Rewrite `test_sync.py` so the existing test cases call the async API (asyncio.run
   or pytest-style wrappers) and still pass. Do not delete test cases.
