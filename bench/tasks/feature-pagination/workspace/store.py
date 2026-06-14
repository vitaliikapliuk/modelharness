class ItemStore:
    """Append-only store. Items are dicts with a unique integer 'id'."""

    def __init__(self, items=None):
        self._items = list(items or [])

    def all_items(self):
        """Items in insertion order."""
        return list(self._items)
