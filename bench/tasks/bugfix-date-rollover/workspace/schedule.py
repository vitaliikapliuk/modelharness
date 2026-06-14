import datetime


def next_monthly(day_of_month: int, after: datetime.date) -> datetime.date:
    """Next date strictly after `after` with the given day of month (clamped)."""
    candidate = after.replace(day=day_of_month)
    if candidate <= after:
        candidate = candidate.replace(month=after.month + 1)
    return candidate
