import calendar
import datetime


def next_monthly(day_of_month: int, after: datetime.date) -> datetime.date:
    """Next date strictly after `after` with the given day of month (clamped)."""
    year, month = after.year, after.month
    while True:
        day = min(day_of_month, calendar.monthrange(year, month)[1])
        candidate = datetime.date(year, month, day)
        if candidate > after:
            return candidate
        month += 1
        if month == 13:
            month, year = 1, year + 1
