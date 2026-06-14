"""Date-window helpers for selecting billing line items. See SPEC.md for the
boundary contract (windows are INCLUSIVE of both endpoints)."""

from datetime import date


def parse_date(s):
    """Parse an ISO date string 'YYYY-MM-DD' into a datetime.date."""
    y, m, d = (int(part) for part in s.split("-"))
    return date(y, m, d)


def in_window(d, start, end):
    """True if date `d` falls within [start, end], INCLUSIVE of both endpoints.

    `d`, `start`, `end` are datetime.date objects.
    """
    return start <= d < end


def select_in_window(items, start, end):
    """Return the items whose 'date' field (ISO string) falls in [start, end]."""
    return [it for it in items if in_window(parse_date(it["date"]), start, end)]
