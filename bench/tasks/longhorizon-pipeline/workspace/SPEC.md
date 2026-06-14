# pipeline spec — module pipeline.py

## Stage 1: parse_line(line: str) -> dict | None
Input lines look like: `2026-06-01T10:00:00Z GET /api/users 200 153ms`
(timestamp, method, path, status, duration). Return
`{"ts": str, "method": str, "path": str, "status": int, "ms": int}`.
Return None for malformed lines (wrong field count, non-integer status/duration,
duration not ending in "ms"). Never raise.

## Stage 2: aggregate(lines: list[str]) -> dict
Parse all lines (skipping None). Return a dict keyed by path:
`{path: {"count": int, "errors": int, "p95_ms": int}}` where errors counts
status >= 500, and p95_ms is the 95th percentile of durations computed as:
sorted durations, index `ceil(0.95 * n) - 1`.

## Stage 3: render_report(agg: dict) -> str
Markdown table sorted by count descending, then path ascending:

    | path | count | errors | p95_ms |
    |---|---|---|---|
    | /api/users | 12 | 1 | 153 |

Exactly this header; one row per path; integer cells; no trailing whitespace.
