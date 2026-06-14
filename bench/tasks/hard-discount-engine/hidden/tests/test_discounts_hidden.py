import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from discounts import compute_price


# ---- single-rule tests -------------------------------------------------


def test_rule18_no_coupons_no_tier():
    assert compute_price(10000, {"tier": "none"}, {"items": 3}, []) == {
        "final_cents": 10000,
        "applied": [],
        "rejected": [],
    }


def test_rule12_empty_cart_all_rejected_even_dup_and_invalid():
    # items == 0: every coupon rejected empty_cart, no dup/invalid sub-classification,
    # no tier discount applied.
    out = compute_price(
        10000,
        {"tier": "gold"},
        {"items": 0},
        [{"code": "A", "kind": "pct", "value": 1000}, {"code": "A", "kind": "x", "value": 0}],
    )
    assert out == {
        "final_cents": 10000,
        "applied": [],
        "rejected": [("A", "empty_cart"), ("A", "empty_cart")],
    }


def test_rule7_gold_tier():
    out = compute_price(10000, {"tier": "gold"}, {"items": 1}, [])
    assert out == {"final_cents": 9500, "applied": ["tier:gold"], "rejected": []}


def test_rule7_silver_tier():
    out = compute_price(10000, {"tier": "silver"}, {"items": 1}, [])
    assert out == {"final_cents": 9750, "applied": ["tier:silver"], "rejected": []}


def test_rule1_round_half_up_silver():
    # 333 * 0.025 = 8.325 -> 8 ; 333 - 8 = 325
    out = compute_price(333, {"tier": "silver"}, {"items": 1}, [])
    assert out["final_cents"] == 325


def test_rule1_step_rounding_two_pct():
    # 1000 -> -33 (33.3) -> 967 -> -32 (32.2) -> 935
    out = compute_price(
        1000,
        {"tier": "none"},
        {"items": 1},
        [{"code": "A", "kind": "pct", "value": 333}, {"code": "B", "kind": "pct", "value": 333}],
    )
    assert out == {"final_cents": 935, "applied": ["A", "B"], "rejected": []}


def test_rule2_pct_before_fixed_reorder():
    # input order: fixed then pct; pct must apply first
    out = compute_price(
        10000,
        {"tier": "none"},
        {"items": 1},
        [{"code": "F", "kind": "fixed", "value": 1000}, {"code": "P", "kind": "pct", "value": 1000}],
    )
    assert out == {"final_cents": 8000, "applied": ["P", "F"], "rejected": []}


def test_rule6_pct_too_large_and_boundary():
    rej = compute_price(10000, {"tier": "none"}, {"items": 1}, [{"code": "P", "kind": "pct", "value": 5001}])
    assert rej == {"final_cents": 10000, "applied": [], "rejected": [("P", "pct_too_large")]}
    ok = compute_price(10000, {"tier": "none"}, {"items": 1}, [{"code": "P", "kind": "pct", "value": 5000}])
    assert ok == {"final_cents": 5000, "applied": ["P"], "rejected": []}


def test_rule10_duplicate():
    out = compute_price(
        10000,
        {"tier": "none"},
        {"items": 1},
        [{"code": "P", "kind": "pct", "value": 1000}, {"code": "P", "kind": "pct", "value": 2000}],
    )
    assert out == {"final_cents": 9000, "applied": ["P"], "rejected": [("P", "duplicate")]}


def test_rule11_invalid_kind():
    out = compute_price(10000, {"tier": "none"}, {"items": 1}, [{"code": "Z", "kind": "bogus", "value": 1}])
    assert out == {"final_cents": 10000, "applied": [], "rejected": [("Z", "invalid")]}


def test_rule5_min_cart_running_price():
    # P pct 1000 -> running 9000; Q fixed needs min_cart 9500 > 9000 -> min_cart reject
    out = compute_price(
        10000,
        {"tier": "none"},
        {"items": 1},
        [{"code": "P", "kind": "pct", "value": 1000}, {"code": "Q", "kind": "fixed", "value": 100, "min_cart_cents": 9500}],
    )
    assert out == {"final_cents": 9000, "applied": ["P"], "rejected": [("Q", "min_cart")]}


def test_rule8_later_smaller_fits_after_cap():
    out = compute_price(
        1000,
        {"tier": "none"},
        {"items": 1},
        [
            {"code": "P", "kind": "pct", "value": 5000},
            {"code": "F", "kind": "fixed", "value": 200},
            {"code": "G", "kind": "fixed", "value": 50},
        ],
    )
    assert out == {"final_cents": 450, "applied": ["P", "G"], "rejected": [("F", "cap_exceeded")]}


def test_rule13_duplicate_beats_invalid():
    out = compute_price(
        10000,
        {"tier": "none"},
        {"items": 1},
        [{"code": "P", "kind": "pct", "value": 1000}, {"code": "P", "kind": "bogus", "value": 0}],
    )
    assert out == {"final_cents": 9000, "applied": ["P"], "rejected": [("P", "duplicate")]}


def test_rule16_fixed_applies_under_cap_no_clamp():
    out = compute_price(1000, {"tier": "none"}, {"items": 1}, [{"code": "F", "kind": "fixed", "value": 600}])
    assert out == {"final_cents": 400, "applied": ["F"], "rejected": []}


# ---- interaction tests -------------------------------------------------


def test_interaction_tier_plus_cap_rejects():
    # base 1000 cap=600. gold removes 50. fixed 600 -> 50+600=650 > 600 -> cap_exceeded
    out = compute_price(1000, {"tier": "gold"}, {"items": 1}, [{"code": "F", "kind": "fixed", "value": 600}])
    assert out == {"final_cents": 950, "applied": ["tier:gold"], "rejected": [("F", "cap_exceeded")]}


def test_interaction_tier_plus_cap_exact_fit():
    # gold removes 50; fixed 550 -> 50+550=600 == cap, fits -> running 950-550=400
    out = compute_price(1000, {"tier": "gold"}, {"items": 1}, [{"code": "F", "kind": "fixed", "value": 550}])
    assert out == {"final_cents": 400, "applied": ["tier:gold", "F"], "rejected": []}


def test_interaction_reorder_then_running_min_cart():
    # input: fixed(min_cart 900) then pct 2000. pct applies first -> running 800;
    # fixed min_cart 900 > 800 -> min_cart reject
    out = compute_price(
        1000,
        {"tier": "none"},
        {"items": 1},
        [
            {"code": "F", "kind": "fixed", "value": 100, "min_cart_cents": 900},
            {"code": "P", "kind": "pct", "value": 2000},
        ],
    )
    assert out == {"final_cents": 800, "applied": ["P"], "rejected": [("F", "min_cart")]}


def test_interaction_non_stackable_first_blocks_all_later():
    out = compute_price(
        10000,
        {"tier": "none"},
        {"items": 1},
        [
            {"code": "X", "kind": "pct", "value": 1000, "stackable": False},
            {"code": "Y", "kind": "pct", "value": 1000},
            {"code": "Z", "kind": "fixed", "value": 500},
        ],
    )
    assert out == {
        "final_cents": 9000,
        "applied": ["X"],
        "rejected": [("Y", "blocked_by_exclusive"), ("Z", "blocked_by_exclusive")],
    }


def test_interaction_not_stackable_middle_then_later_applies():
    out = compute_price(
        10000,
        {"tier": "none"},
        {"items": 1},
        [
            {"code": "A", "kind": "pct", "value": 1000},
            {"code": "B", "kind": "pct", "value": 1000, "stackable": False},
            {"code": "C", "kind": "pct", "value": 1000},
        ],
    )
    assert out == {"final_cents": 8100, "applied": ["A", "C"], "rejected": [("B", "not_stackable")]}


def test_interaction_clamp_applies_cap_uses_preclamp():
    # base 100 cap=60. fixed 55 <= cap, applies; running-50=50, 55>50 -> clamp to 50
    out = compute_price(100, {"tier": "none"}, {"items": 1}, [{"code": "F", "kind": "fixed", "value": 55}])
    assert out == {"final_cents": 50, "applied": ["F"], "rejected": []}


def test_interaction_clamp_cap_rejects_on_preclamp():
    # base 100 cap=60. fixed 65 > cap on pre-clamp -> cap_exceeded even though clamp
    # would only remove 50.
    out = compute_price(100, {"tier": "none"}, {"items": 1}, [{"code": "F", "kind": "fixed", "value": 65}])
    assert out == {"final_cents": 100, "applied": [], "rejected": [("F", "cap_exceeded")]}
