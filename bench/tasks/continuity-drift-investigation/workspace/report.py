"""Build a billing report for a date window. Orchestrates dates/categorize/money.
See SPEC.md for the report shape and worked examples."""

from dates import select_in_window, parse_date
from categorize import categorize
from money import round_money


def build_report(items, start_str, end_str):
    """Build a report over the items dated within [start_str, end_str] inclusive.

    Each item is a dict: {"date": "YYYY-MM-DD", "kind": str, "amount": float}.

    Returns:
        {
          "window": {"start": start_str, "end": end_str},
          "totals": {"charges": float, "credits": float, "fees": float},
          "net": float,          # charges - credits + fees, rounded to cents
          "count": int,          # number of items in the window
        }

    Per-category totals are the round_money sum of that category's item amounts.
    `net` is computed from the (already rounded) category totals and rounded again.
    """
    start = parse_date(start_str)
    end = parse_date(end_str)
    selected = select_in_window(items, start, end)

    totals = {"charges": 0.0, "credits": 0.0, "fees": 0.0}
    for it in selected:
        cat = categorize(it)
        totals[cat] = round_money(totals[cat] + round_money(it["amount"]))

    net = round_money(totals["charges"] - totals["credits"] + totals["fees"])
    return {
        "window": {"start": start_str, "end": end_str},
        "totals": totals,
        "net": net,
        "count": len(selected),
    }
