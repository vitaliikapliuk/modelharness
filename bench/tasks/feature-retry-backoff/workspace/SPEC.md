# retry decorator spec

`retry(times, base_delay, max_delay, retry_on, sleep=time.sleep)` returns a decorator.

- Calls the wrapped function; on an exception that is an instance of `retry_on`
  (an exception class or tuple), retries up to `times` additional attempts.
- Delay before retry k (k=1..times) is `min(base_delay * 2**(k-1), max_delay)`,
  passed to `sleep`.
- Exceptions NOT matching `retry_on` propagate immediately, no retry, no sleep.
- If all attempts fail, the LAST exception propagates.
- On success, returns the wrapped function's return value; no further sleeps.
- The decorator preserves the wrapped function's `__name__` (functools.wraps).
