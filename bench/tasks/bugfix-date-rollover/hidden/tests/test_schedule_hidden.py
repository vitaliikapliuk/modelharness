import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import datetime
from schedule import next_monthly


def test_rolls_to_next_month():
    assert next_monthly(5, datetime.date(2026, 6, 10)) == datetime.date(2026, 7, 5)


def test_clamps_short_month():
    assert next_monthly(31, datetime.date(2026, 1, 31)) == datetime.date(2026, 2, 28)


def test_leap_february():
    assert next_monthly(30, datetime.date(2028, 1, 31)) == datetime.date(2028, 2, 29)


def test_year_rollover():
    assert next_monthly(15, datetime.date(2026, 12, 20)) == datetime.date(2027, 1, 15)


def test_strictly_after_same_day():
    assert next_monthly(10, datetime.date(2026, 6, 10)) == datetime.date(2026, 7, 10)
