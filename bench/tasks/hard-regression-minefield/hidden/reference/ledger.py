"""In-memory ledger keyed by canonical id."""

from normalizer import normalize_id


class Ledger:
    def __init__(self):
        self._records = {}

    def add(self, raw_id: str, amount: int) -> str:
        # Build the storage key from the raw id, then accumulate the amount onto
        # any existing balance for that key. Returns the key actually used.
        key = normalize_id(raw_id)
        if not key:
            raise ValueError("empty id")
        prior = self._records.get(_canonical_key(key), 0)
        stored_key = _canonical_key(key)
        self._records[stored_key] = prior + amount
        return stored_key

    def balance(self, raw_id: str) -> int:
        key = _canonical_key(normalize_id(raw_id))
        return self._records.get(key, 0)

    def keys(self):
        return sorted(self._records)


def _canonical_key(key: str) -> str:
    # normalize_id now returns the canonical id directly
    return key
