"""Hidden acceptance tests for continuity-staged-build (>=18 tests).

Stage A unit rules, Stage B over Stage A's valid output, Stage C, and the full
end-to-end pipeline. Public signatures/behavior are pinned by SPEC.md; internal
data shapes are the implementer's choice and are not asserted here.
"""

from stage_a import validate_record, validate_all
from stage_b import transform_all
from stage_c import summarize
from pipeline import run_pipeline


# ---------------- Stage A: individual rule types ----------------

def test_a_required():
    rules = [{"type": "required", "field": "id"}]
    assert validate_record({"id": "x"}, rules) == (True, [])
    assert validate_record({}, rules) == (False, ["required:id"])
    assert validate_record({"id": None}, rules) == (False, ["required:id"])


def test_a_type_and_bool_is_not_int():
    rules = [{"type": "type", "field": "qty", "py": "int"}]
    assert validate_record({"qty": 3}, rules) == (True, [])
    assert validate_record({"qty": 3.0}, rules) == (False, ["type:qty"])
    assert validate_record({"qty": True}, rules) == (False, ["type:qty"])
    assert validate_record({}, rules) == (True, [])  # absent non-required -> skip


def test_a_min_max():
    rules = [{"type": "min", "field": "n", "value": 0},
             {"type": "max", "field": "n", "value": 10}]
    assert validate_record({"n": 5}, rules) == (True, [])
    assert validate_record({"n": -1}, rules) == (False, ["min:n"])
    assert validate_record({"n": 11}, rules) == (False, ["max:n"])


def test_a_non_empty():
    rules = [{"type": "non_empty", "field": "tags"}]
    assert validate_record({"tags": ["a"]}, rules) == (True, [])
    assert validate_record({"tags": []}, rules) == (False, ["non_empty:tags"])
    assert validate_record({"tags": ""}, rules) == (False, ["non_empty:tags"])


def test_a_enum():
    rules = [{"type": "enum", "field": "status", "allowed": ["new", "paid"]}]
    assert validate_record({"status": "paid"}, rules) == (True, [])
    assert validate_record({"status": "x"}, rules) == (False, ["enum:status"])


def test_a_regex():
    rules = [{"type": "regex", "field": "id", "pattern": r"r\d+"}]
    assert validate_record({"id": "r12"}, rules) == (True, [])
    assert validate_record({"id": "x12"}, rules) == (False, ["regex:id"])
    assert validate_record({"id": "r12x"}, rules) == (False, ["regex:id"])  # fullmatch


def test_a_max_len():
    rules = [{"type": "max_len", "field": "id", "value": 3}]
    assert validate_record({"id": "abc"}, rules) == (True, [])
    assert validate_record({"id": "abcd"}, rules) == (False, ["max_len:id"])


def test_a_positive():
    rules = [{"type": "positive", "field": "qty"}]
    assert validate_record({"qty": 1}, rules) == (True, [])
    assert validate_record({"qty": 0}, rules) == (False, ["positive:qty"])
    assert validate_record({"qty": -2}, rules) == (False, ["positive:qty"])


def test_a_in_set_scalar_and_list():
    rules = [{"type": "in_set", "field": "tags", "set": ["a", "b", "c"]}]
    assert validate_record({"tags": ["a", "c"]}, rules) == (True, [])
    assert validate_record({"tags": ["a", "z"]}, rules) == (False, ["in_set:tags"])
    scalar = [{"type": "in_set", "field": "region", "set": ["us", "eu"]}]
    assert validate_record({"region": "us"}, scalar) == (True, [])
    assert validate_record({"region": "zz"}, scalar) == (False, ["in_set:region"])


def test_a_errors_sorted_unique():
    rules = [{"type": "required", "field": "id"},
             {"type": "positive", "field": "qty"},
             {"type": "enum", "field": "status", "allowed": ["new"]}]
    ok, errs = validate_record({"qty": -1, "status": "bad"}, rules)
    assert ok is False
    assert errs == ["enum:status", "positive:qty", "required:id"]


def test_a_worked_example():
    rules = [{"type": "required", "field": "id"},
             {"type": "type", "field": "qty", "py": "int"},
             {"type": "positive", "field": "qty"},
             {"type": "enum", "field": "status", "allowed": ["new", "paid", "void"]}]
    assert validate_record({"id": "r1", "qty": 3, "status": "paid"}, rules) == (True, [])


def test_a_validate_all_split_and_order():
    rules = [{"type": "required", "field": "id"}]
    recs = [{"id": "a"}, {"x": 1}, {"id": "c"}]
    out = validate_all(recs, rules)
    assert out["valid"] == [{"id": "a"}, {"id": "c"}]
    assert out["rejected"] == [{"id": None, "errors": ["required:id"]}]


# ---------------- Stage B over Stage A output ----------------

def test_b_does_not_mutate_input():
    src = [{"region": "us"}]
    transform_all(src, [{"type": "upper", "field": "region"}])
    assert src == [{"region": "us"}]


def test_b_rename_default_drop():
    rules = [{"type": "rename", "from": "amount", "to": "amt"},
             {"type": "default", "field": "qty", "value": 1},
             {"type": "drop", "field": "junk"}]
    out = transform_all([{"amount": 5, "junk": 9}], rules)
    assert out == [{"amt": 5, "qty": 1}]


def test_b_derive_scale_round():
    rules = [{"type": "derive_total", "qty": "qty", "price": "price", "to": "total"},
             {"type": "scale", "field": "total", "by": 1.1},
             {"type": "round", "field": "total", "ndigits": 2}]
    out = transform_all([{"qty": 2, "price": 10.0}], rules)
    assert out[0]["total"] == 22.0


def test_b_tag_no_duplicate_and_creates_list():
    rules = [{"type": "tag", "field": "tags", "add": "processed"}]
    assert transform_all([{"tags": ["a"]}], rules)[0]["tags"] == ["a", "processed"]
    assert transform_all([{}], rules)[0]["tags"] == ["processed"]
    assert transform_all([{"tags": ["processed"]}], rules)[0]["tags"] == ["processed"]


def test_b_worked_example():
    rules = [{"type": "default", "field": "qty", "value": 1},
             {"type": "derive_total", "qty": "qty", "price": "price", "to": "total"},
             {"type": "scale", "field": "total", "by": 1.1},
             {"type": "round", "field": "total", "ndigits": 2},
             {"type": "upper", "field": "region"},
             {"type": "tag", "field": "tags", "add": "processed"}]
    out = transform_all([{"price": 10.0, "qty": 2, "region": "us", "tags": ["a"]}], rules)
    assert out == [{"price": 10.0, "qty": 2, "region": "US",
                    "tags": ["a", "processed"], "total": 22.0}]


def test_b_chains_after_validation():
    a_rules = [{"type": "required", "field": "id"}]
    b_rules = [{"type": "upper", "field": "region"}]
    valid = validate_all([{"id": "1", "region": "us"}, {"region": "eu"}], a_rules)["valid"]
    out = transform_all(valid, b_rules)
    assert out == [{"id": "1", "region": "US"}]


# ---------------- Stage C ----------------

def test_c_empty():
    s = summarize([])
    assert s["count"] == 0
    assert s["total_sum"] == 0.0
    assert s["by_category"] == {}
    assert s["regions"] == []
    assert s["max_total"] is None
    assert s["tag_counts"] == {}


def test_c_aggregations():
    recs = [
        {"total": 10.0, "category": "x", "region": "US", "tags": ["p", "q"]},
        {"total": 5.5, "category": "x", "region": "EU", "tags": ["p"]},
        {"category": "y", "region": "US", "tags": []},
    ]
    s = summarize(recs)
    assert s["count"] == 3
    assert s["total_sum"] == 15.5
    assert s["by_category"] == {"x": 2, "y": 1}
    assert s["regions"] == ["EU", "US"]
    assert s["max_total"] == 10.0
    assert s["tag_counts"] == {"p": 2, "q": 1}


# ---------------- End-to-end pipeline (Stage C consuming A->B) ----------------

def test_pipeline_end_to_end():
    config = {
        "validation": [
            {"type": "required", "field": "id"},
            {"type": "positive", "field": "qty"},
            {"type": "enum", "field": "status", "allowed": ["new", "paid"]},
        ],
        "transform": [
            {"type": "default", "field": "qty", "value": 1},
            {"type": "derive_total", "qty": "qty", "price": "price", "to": "total"},
            {"type": "round", "field": "total", "ndigits": 2},
            {"type": "upper", "field": "region"},
            {"type": "tag", "field": "tags", "add": "processed"},
        ],
    }
    records = [
        {"id": "a", "qty": 2, "price": 3.0, "status": "paid", "category": "c1",
         "region": "us", "tags": []},
        {"id": "b", "qty": 1, "price": 10.0, "status": "new", "category": "c1",
         "region": "eu", "tags": ["vip"]},
        {"qty": 1, "price": 1.0, "status": "paid"},        # rejected: missing id
        {"id": "d", "qty": -1, "price": 1.0, "status": "x"},  # rejected: qty + status
    ]
    out = run_pipeline(records, config)

    assert out["rejected"] == [
        {"id": None, "errors": ["required:id"]},
        {"id": "d", "errors": ["enum:status", "positive:qty"]},
    ]
    s = out["summary"]
    assert s["count"] == 2
    assert s["total_sum"] == 16.0          # 6.0 + 10.0
    assert s["max_total"] == 10.0
    assert s["by_category"] == {"c1": 2}
    assert s["regions"] == ["EU", "US"]
    assert s["tag_counts"] == {"processed": 2, "vip": 1}
