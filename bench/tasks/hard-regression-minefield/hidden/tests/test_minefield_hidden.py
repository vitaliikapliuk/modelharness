import sys
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from normalizer import normalize_id
from ledger import Ledger
from matcher import find_match
from report import render


# ---- (1) normalize_id matches its documented contract (no reversal) ----


def test_normalize_id_matches_docstring_no_reversal():
    cases = {
        "Foo-Bar_1": "foobar1",
        "ABC": "abc",
        "a.b.c": "abc",
        "Hello World": "helloworld",
        "x_Y-z": "xyz",
        "Order-12_3": "order123",
    }
    for raw, expected in cases.items():
        assert normalize_id(raw) == expected, (raw, normalize_id(raw))


def test_normalize_id_is_not_reversed():
    # A value that is NOT a palindrome distinguishes correct from reversed output.
    assert normalize_id("abcdef") == "abcdef"


# ---- (2) source check: workarounds removed from ledger and matcher ----


def _src(name):
    return (ROOT / name).read_text()


def test_ledger_has_no_reversal_workaround():
    src = _src("ledger.py")
    assert "[::-1]" not in src
    assert not re.search(r"reversed\s*\(", src)


def test_matcher_has_no_reversal_workaround():
    src = _src("matcher.py")
    assert "[::-1]" not in src
    assert not re.search(r"reversed\s*\(", src)


# ---- (3) end-to-end behavior re-verified through the modules --------


def test_e2e_balance_case_and_separator_insensitive():
    lg = Ledger()
    lg.add("Foo-Bar", 5)
    lg.add("foo.bar", 3)
    assert lg.balance("FOOBAR") == 8
    assert lg.balance("f_o_o_b_a_r") == 8


def test_e2e_add_returns_stored_key():
    lg = Ledger()
    key = lg.add("Order-12_3", 10)
    assert key == "order123"
    assert key in lg.keys()
    assert lg.balance("order123") == 10


def test_e2e_report_renders_canonical_keys():
    lg = Ledger()
    lg.add("Widget-A", 7)
    lg.add("Widget-B", 2)
    out = render(lg)
    assert out == "widgeta: 7\nwidgetb: 2"


def test_e2e_matcher_exact_and_prefix():
    lg = Ledger()
    lg.add("Customer-99", 1)
    lg.add("invoice-2024", 1)
    lg.add("payment-2024", 1)
    keys = lg.keys()
    assert find_match("CUSTOMER99", keys) == "customer99"
    assert find_match("invoice", keys) == "invoice2024"
    assert find_match("totally-different", keys) is None


def test_e2e_keys_are_canonical_unreversed():
    lg = Ledger()
    lg.add("abcdef", 1)
    # the stored key is the canonical id, not its reverse
    assert lg.keys() == ["abcdef"]
