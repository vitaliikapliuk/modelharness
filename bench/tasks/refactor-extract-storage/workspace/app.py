"""Tiny order tracker: add orders, list by user, compute totals. (Needs refactoring.)"""

_ORDERS = {}
_NEXT_ID = [1]


def add_order(user: str, amount: float) -> int:
    if not user:
        raise ValueError("user required")
    if amount <= 0:
        raise ValueError("amount must be positive")
    order_id = _NEXT_ID[0]
    _NEXT_ID[0] += 1
    _ORDERS[order_id] = {"id": order_id, "user": user, "amount": round(amount, 2)}
    return order_id


def orders_for(user: str) -> list:
    found = []
    for order in _ORDERS.values():
        if order["user"] == user:
            found.append(dict(order))
    return sorted(found, key=lambda o: o["id"])


def user_total(user: str) -> str:
    total = 0.0
    for order in _ORDERS.values():
        if order["user"] == user:
            total += order["amount"]
    return f"{user}: ${total:.2f}"


def reset() -> None:
    _ORDERS.clear()
    _NEXT_ID[0] = 1
