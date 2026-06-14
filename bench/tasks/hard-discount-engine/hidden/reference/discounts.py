"""Reference solution for the discount engine (SPEC.md)."""

from decimal import Decimal, ROUND_HALF_UP

MIN_CHARGE = 50
PCT_CAP_BP = 5000


def _round_half_up(amount_cents, value_bp):
    """round_half_up(amount * value_bp / 10000), ties away from zero."""
    q = Decimal(amount_cents) * Decimal(value_bp) / Decimal(10000)
    return int(q.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def compute_price(base_cents, customer, cart, coupons):
    # --- evaluation order (rule 2): stable, pct before fixed ---
    indexed = list(enumerate(coupons))

    def sort_key(item):
        i, c = item
        kind = c.get("kind")
        # pct (0) before fixed (1) before everything else (2); stable by index
        if kind == "pct":
            bucket = 0
        elif kind == "fixed":
            bucket = 1
        else:
            bucket = 2
        return (bucket, i)

    order = [c for _, c in sorted(indexed, key=sort_key)]

    applied = []
    rejected = []

    # --- rule 12: empty cart short-circuit ---
    if cart.get("items", 0) == 0:
        for c in order:
            rejected.append((c.get("code"), "empty_cart"))
        return {"final_cents": base_cents, "applied": applied, "rejected": rejected}

    running = base_cents
    removed_total = 0  # cumulative pre-clamp removed cents (rule 17)

    # --- rule 7: tier discount, before any coupon ---
    tier = customer.get("tier")
    if tier == "gold":
        d = _round_half_up(running, 500)
        running -= d
        removed_total += d
        applied.append("tier:gold")
    elif tier == "silver":
        d = _round_half_up(running, 250)
        running -= d
        removed_total += d
        applied.append("tier:silver")

    cap = (base_cents * 60) // 100  # floor(base * 0.60)

    seen_codes = set()
    exclusive_block = False  # set once a non-stackable coupon applies (rule 4)

    for c in order:
        code = c.get("code")
        kind = c.get("kind")
        stackable = c.get("stackable", True)
        min_cart = c.get("min_cart_cents", 0)

        # rule 13 precedence: duplicate > invalid > blocked > not_stackable
        #   > pct_too_large > min_cart > cap_exceeded
        if code in seen_codes:
            rejected.append((code, "duplicate"))
            continue
        seen_codes.add(code)

        if kind not in ("pct", "fixed"):
            rejected.append((code, "invalid"))
            continue

        if exclusive_block:
            rejected.append((code, "blocked_by_exclusive"))
            continue

        if not stackable and len(applied_coupons(applied)) > 0:
            rejected.append((code, "not_stackable"))
            continue

        if kind == "pct" and c.get("value", 0) > PCT_CAP_BP:
            rejected.append((code, "pct_too_large"))
            continue

        # rule 5: min_cart against running price
        if running < min_cart:
            rejected.append((code, "min_cart"))
            continue

        # compute pre-clamp removal
        if kind == "pct":
            removal = _round_half_up(running, c.get("value", 0))
        else:  # fixed
            removal = c.get("value", 0)

        # rule 8 / 17: cap check on pre-clamp cumulative removed cents
        if removed_total + removal > cap:
            rejected.append((code, "cap_exceeded"))
            continue

        # apply
        if kind == "pct":
            running -= removal
            removed_total += removal
        else:  # fixed, with clamp (rule 9 / 16)
            actual = running - MIN_CHARGE
            if actual < 0:
                actual = 0
            if removal <= actual:
                running -= removal
            else:
                running = MIN_CHARGE
            removed_total += removal  # rule 17: full pre-clamp value

        applied.append(code)

        if not stackable:
            exclusive_block = True

    return {"final_cents": running, "applied": applied, "rejected": rejected}


def applied_coupons(applied):
    """Applied entries that are coupon codes (exclude tier:* entries)."""
    return [a for a in applied if not str(a).startswith("tier:")]
