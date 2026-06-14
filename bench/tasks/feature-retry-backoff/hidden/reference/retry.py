import functools
import time


def retry(times, base_delay, max_delay, retry_on, sleep=time.sleep):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times + 1):
                try:
                    return fn(*args, **kwargs)
                except retry_on:
                    if attempt == times:
                        raise
                    sleep(min(base_delay * 2 ** attempt, max_delay))
        return wrapper
    return decorator
