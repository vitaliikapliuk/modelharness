"""Visible end-to-end tests. These pin observable behavior of the system as a whole.

They must keep passing after normalize_id is fixed to match its docstring. They do
NOT assert anything about the (buggy) reversal — only end-to-end results.
"""

from ledger import Ledger
from matcher import find_match
from report import render


def test_balance_is_case_and_separator_insensitive():
    lg = Ledger()
    lg.add("Foo-Bar", 5)
    lg.add("foo.bar", 3)
    # same canonical id -> balances accumulate
    assert lg.balance("FOOBAR") == 8
    assert lg.balance("f_o_o_b_a_r") == 8


def test_distinct_ids_are_separate():
    lg = Ledger()
    lg.add("alpha", 1)
    lg.add("beta", 2)
    assert lg.balance("ALPHA") == 1
    assert lg.balance("Beta") == 2


def test_add_returns_stored_key_used_by_balance():
    lg = Ledger()
    key = lg.add("Order-12_3", 10)
    # the key returned by add is exactly the key balance() looks up
    assert lg.balance("order123") == 10
    assert key in lg.keys()


def test_report_renders_keys_and_balances():
    lg = Ledger()
    lg.add("Widget-A", 7)
    lg.add("Widget-B", 2)
    out = render(lg)
    assert "widgeta: 7" in out
    assert "widgetb: 2" in out


def test_matcher_exact_match():
    lg = Ledger()
    lg.add("Customer-99", 1)
    keys = lg.keys()
    assert find_match("CUSTOMER99", keys) == "customer99"
    assert find_match("customer.99", keys) == "customer99"


def test_matcher_unique_prefix_match():
    lg = Ledger()
    lg.add("invoice-2024", 1)
    lg.add("payment-2024", 1)
    keys = lg.keys()
    # "invoice" is a unique prefix of exactly one key
    assert find_match("invoice", keys) == "invoice2024"


def test_matcher_no_match_returns_none():
    lg = Ledger()
    lg.add("known-id", 1)
    keys = lg.keys()
    assert find_match("totally-different", keys) is None


def test_empty_id_rejected():
    lg = Ledger()
    try:
        lg.add("---", 1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for empty id")
