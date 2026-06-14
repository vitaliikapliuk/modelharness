"""Hidden acceptance tests for continuity-drift-investigation.

Three subtle interacting defects were planted across money.py, dates.py and
categorize.py. SPEC.md's worked examples are the ground truth. These tests pin:
  - each defect in isolation (so a partial fix is detectable), and
  - the full worked-example report dicts from SPEC.md.
"""

from data import ITEMS
from report import build_report
from money import round_money
from dates import parse_date, in_window
from categorize import categorize


# --- Defect 1: money rounding must be round-half-up, not truncation ---

def test_round_half_up_basic():
    assert round_money(12.345) == 12.35
    assert round_money(4.005) == 4.01
    assert round_money(1.255) == 1.26
    assert round_money(2.005) == 2.01
    assert round_money(3.125) == 3.13


def test_round_does_not_change_exact_cents():
    assert round_money(30.00) == 30.00
    assert round_money(5.00) == 5.00


# --- Defect 2: date window is inclusive of BOTH endpoints ---

def test_window_includes_end_date():
    d = parse_date("2024-01-31")
    assert in_window(d, parse_date("2024-01-01"), parse_date("2024-01-31"))


def test_full_january_count_includes_jan_31():
    # Jan 1..Jan 31 inclusive contains 7 items (the Jan 31 discount must be counted).
    r = build_report(ITEMS, "2024-01-01", "2024-01-31")
    assert r["count"] == 7


# --- Defect 3: 'adjustment' is a credit, not a fee ---

def test_adjustment_is_a_credit():
    assert categorize({"kind": "adjustment"}) == "credits"


def test_fees_only_contain_third_party_kinds():
    for kind in ("processing", "gateway"):
        assert categorize({"kind": kind}) == "fees"


# --- Full worked examples from SPEC.md (interaction of all three fixes) ---

def test_worked_example_1():
    assert build_report(ITEMS, "2024-01-01", "2024-01-31") == {
        "window": {"start": "2024-01-01", "end": "2024-01-31"},
        "totals": {"charges": 46.36, "credits": 10.14, "fees": 1.26},
        "net": 37.48,
        "count": 7,
    }


def test_worked_example_2():
    assert build_report(ITEMS, "2024-01-10", "2024-01-25") == {
        "window": {"start": "2024-01-10", "end": "2024-01-25"},
        "totals": {"charges": 4.01, "credits": 7.01, "fees": 1.26},
        "net": -1.74,
        "count": 4,
    }
