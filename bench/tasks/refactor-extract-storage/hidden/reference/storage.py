class Storage:
    """Owns all order state."""

    def __init__(self):
        self._orders = {}
        self._next_id = 1

    def insert(self, record: dict) -> int:
        order_id = self._next_id
        self._next_id += 1
        self._orders[order_id] = {"id": order_id, **record}
        return order_id

    def by_user(self, user: str) -> list:
        return sorted(
            (dict(o) for o in self._orders.values() if o["user"] == user),
            key=lambda o: o["id"],
        )

    def clear(self):
        self._orders.clear()
        self._next_id = 1
