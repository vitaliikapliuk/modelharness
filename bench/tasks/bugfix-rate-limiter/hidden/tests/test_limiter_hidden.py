import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from limiter import TokenBucket


def make(capacity=3, rate=1.0):
    t = [0.0]
    return TokenBucket(capacity=capacity, rate=rate, clock=lambda: t[0]), t


def test_denies_burst_beyond_capacity():
    b, t = make(capacity=3)
    assert b.allow() and b.allow() and b.allow()
    assert b.allow() is False  # 4th immediate request must be denied


def test_refill_is_proportional_to_elapsed_time():
    b, t = make(capacity=3, rate=1.0)
    for _ in range(3):
        b.allow()
    t[0] += 1.0          # exactly one token refilled
    assert b.allow() is True
    assert b.allow() is False


def test_refill_caps_at_capacity():
    b, t = make(capacity=3, rate=1.0)
    t[0] += 100.0
    allowed = sum(1 for _ in range(10) if b.allow())
    assert allowed == 3
