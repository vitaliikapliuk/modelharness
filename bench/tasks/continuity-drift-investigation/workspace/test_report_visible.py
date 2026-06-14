"""Visible smoke tests for the billing report. These check structural invariants
that must always hold; they do NOT pin the worked-example numbers from SPEC.md
(those are the acceptance bar and live in the hidden grader). These pass on the
untouched workspace."""

from data import ITEMS
from report import build_report
from money import round_money
from dates import parse_date, in_window
from categorize import categorize


def test_window_is_echoed():
    r = build_report(ITEMS, "2024-01-01", "2024-01-31")
    assert r["window"] == {"start": "2024-01-01", "end": "2024-01-31"}


def test_totals_have_three_categories():
    r = build_report(ITEMS, "2024-01-01", "2024-02-28")
    assert set(r["totals"].keys()) == {"charges", "credits", "fees"}


def test_count_matches_items_in_some_window():
    r = build_report(ITEMS, "2024-01-01", "2024-02-28")
    assert isinstance(r["count"], int)
    assert r["count"] >= 1


def test_net_is_derived_from_totals():
    r = build_report(ITEMS, "2024-01-01", "2024-01-31")
    t = r["totals"]
    expected = round_money(t["charges"] - t["credits"] + t["fees"])
    assert r["net"] == expected


def test_round_money_returns_two_places():
    val = round_money(1.239)
    assert abs(val * 100 - round(val * 100)) < 1e-9


def test_categorize_known_kinds():
    # subscription is unambiguously a charge in every version of the spec.
    assert categorize({"kind": "subscription"}) == "charges"


def test_in_window_includes_start():
    d = parse_date("2024-01-10")
    assert in_window(d, parse_date("2024-01-10"), parse_date("2024-01-20"))
