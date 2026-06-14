import time


class TTLCache:
    """In-memory cache where entries expire ttl_seconds after being set."""

    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds
        self._data = {}

    def set(self, key, value):
        self._data[key] = (value, time.monotonic())

    def get(self, key, default=None):
        if key not in self._data:
            return default
        value, stored_at = self._data[key]
        if time.monotonic() - stored_at <= self.ttl:
            return value
        del self._data[key]
        return default

    def size(self):
        return len(self._data)
