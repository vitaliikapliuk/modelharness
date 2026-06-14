"""Tiny order tracker — thin facade over service layer."""

import service


def add_order(user: str, amount: float) -> int:
    return service.add_order(user, amount)


def orders_for(user: str) -> list:
    return service.orders_for(user)


def user_total(user: str) -> str:
    return service.user_total(user)


def reset() -> None:
    service.reset()
