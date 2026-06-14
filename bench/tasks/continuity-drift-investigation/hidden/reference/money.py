"""Money helpers. All monetary amounts are dollars as floats; cents are the
smallest unit. See SPEC.md for the rounding contract."""

from decimal import Decimal, ROUND_HALF_UP


def round_money(amount):
    """Round a dollar amount to whole cents using round-half-up (0.005 -> 0.01).

    Returns a float with at most two decimal places.
    """
    cents = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(cents)


def add_tax(subtotal, rate):
    """Return subtotal plus tax, where tax is `subtotal * rate` rounded to cents.

    The tax is rounded independently before being added (banker's-style line tax),
    then the total is rounded again to guard against float drift.
    """
    tax = round_money(subtotal * rate)
    return round_money(subtotal + tax)
