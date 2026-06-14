"""Discount engine — implement compute_price per SPEC.md."""


def compute_price(base_cents, customer, cart, coupons):
    """Implement per SPEC.md.

    Args:
        base_cents: int
        customer: dict with at least {"tier": str}
        cart: dict with at least {"items": int}
        coupons: list of coupon dicts (see SPEC.md)

    Returns:
        {"final_cents": int, "applied": list[str], "rejected": list[tuple[str, str]]}
    """
    raise NotImplementedError
