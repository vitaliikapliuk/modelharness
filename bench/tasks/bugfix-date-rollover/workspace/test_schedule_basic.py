import datetime
from schedule import next_monthly


def test_same_month_future_day():
    assert next_monthly(20, datetime.date(2026, 6, 10)) == datetime.date(2026, 6, 20)
