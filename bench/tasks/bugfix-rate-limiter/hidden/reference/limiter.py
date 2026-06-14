import time


class TokenBucket:
    """Allows up to `capacity` requests, refilling at `rate` tokens/second."""

    def __init__(self, capacity: float, rate: float, clock=time.monotonic):
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        self.tokens = capacity
        self.last = clock()

    def allow(self) -> bool:
        now = self.clock()
        elapsed = now - self.last
        self.last = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
