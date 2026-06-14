from storage import Storage

store = Storage()


def add_order(user: str, amount: float) -> int:
    if not user:
        raise ValueError("user required")
    if amount <= 0:
        raise ValueError("amount must be positive")
    return store.insert({"user": user, "amount": round(amount, 2)})


def orders_for(user: str) -> list:
    return store.by_user(user)


def user_total(user: str) -> str:
    total = sum(o["amount"] for o in store.by_user(user))
    return f"{user}: ${total:.2f}"


def reset() -> None:
    store.clear()
