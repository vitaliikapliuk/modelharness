import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import pytest
from retry import retry


class Boom(Exception):
    pass


def make_flaky(fail_times, exc=Boom):
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] <= fail_times:
            raise exc("boom")
        return "ok"

    fn.calls = calls
    return fn


def test_succeeds_after_retries_with_exponential_backoff():
    sleeps = []
    fn = retry(times=3, base_delay=1.0, max_delay=10.0, retry_on=Boom,
               sleep=sleeps.append)(make_flaky(2))
    assert fn() == "ok"
    assert sleeps == [1.0, 2.0]


def test_delay_caps_at_max():
    sleeps = []
    fn = retry(times=4, base_delay=3.0, max_delay=5.0, retry_on=Boom,
               sleep=sleeps.append)(make_flaky(5))
    with pytest.raises(Boom):
        fn()
    assert sleeps == [3.0, 5.0, 5.0, 5.0]


def test_non_matching_exception_propagates_immediately():
    sleeps = []
    fn = retry(times=3, base_delay=1.0, max_delay=10.0, retry_on=KeyError,
               sleep=sleeps.append)(make_flaky(1, exc=Boom))
    with pytest.raises(Boom):
        fn()
    assert sleeps == []


def test_no_sleep_on_first_success():
    sleeps = []
    fn = retry(times=3, base_delay=1.0, max_delay=10.0, retry_on=Boom,
               sleep=sleeps.append)(make_flaky(0))
    assert fn() == "ok"
    assert sleeps == []


def test_wraps_preserves_name():
    @retry(times=1, base_delay=0.1, max_delay=1.0, retry_on=Boom, sleep=lambda s: None)
    def my_function():
        return 1

    assert my_function.__name__ == "my_function"
