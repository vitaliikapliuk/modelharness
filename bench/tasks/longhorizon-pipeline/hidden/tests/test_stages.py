import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from pipeline import parse_line, aggregate, render_report


def test_stage1_parses_valid_line():
    assert parse_line("2026-06-01T10:00:00Z GET /api/users 200 153ms") == {
        "ts": "2026-06-01T10:00:00Z", "method": "GET", "path": "/api/users",
        "status": 200, "ms": 153,
    }


def test_stage1_rejects_malformed():
    assert parse_line("garbage") is None
    assert parse_line("2026-06-01T10:00:00Z GET /x abc 153ms") is None
    assert parse_line("2026-06-01T10:00:00Z GET /x 200 153") is None
    assert parse_line("") is None


def test_stage2_aggregates():
    lines = [
        "2026-06-01T10:00:00Z GET /a 200 100ms",
        "2026-06-01T10:00:01Z GET /a 503 300ms",
        "2026-06-01T10:00:02Z GET /a 200 200ms",
        "2026-06-01T10:00:04Z GET /a 404 150ms",
        "bad",
        "2026-06-01T10:00:03Z GET /b 200 50ms",
    ]
    agg = aggregate(lines)
    assert agg["/a"]["count"] == 4
    assert agg["/a"]["errors"] == 1  # 404 is NOT an error (only status >= 500)
    assert agg["/a"]["p95_ms"] == 300  # sorted [100,150,200,300], ceil(0.95*4)-1 = 3
    assert agg["/b"] == {"count": 1, "errors": 0, "p95_ms": 50}


def test_stage3_renders_sorted_table():
    agg = {
        "/b": {"count": 2, "errors": 0, "p95_ms": 10},
        "/a": {"count": 5, "errors": 1, "p95_ms": 99},
        "/c": {"count": 2, "errors": 2, "p95_ms": 20},
    }
    out = render_report(agg)
    lines = out.splitlines()
    assert lines[0] == "| path | count | errors | p95_ms |"
    assert lines[1] == "|---|---|---|---|"
    assert lines[2] == "| /a | 5 | 1 | 99 |"
    assert lines[3] == "| /b | 2 | 0 | 10 |"   # count tie -> path ascending
    assert lines[4] == "| /c | 2 | 2 | 20 |"
    assert all(l == l.rstrip() for l in lines)
