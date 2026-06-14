from limiter import TokenBucket


def test_allows_within_capacity():
    t = [0.0]
    b = TokenBucket(capacity=3, rate=1, clock=lambda: t[0])
    assert b.allow() and b.allow() and b.allow()
