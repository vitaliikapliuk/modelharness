#!/usr/bin/env python3
"""Harness-lift: per-model paired comparison (bare vs +modelharness plugin).

Usage: python3 bench/lift.py [results.csv]
       (default: bench/results/results-v0.2.0.csv)

For each model pair present in the CSV, prints:
  - A markdown table with overall bare→plugin comparison.
  - A per-category drill-down for categories where success rate changed.

Stdlib only.  Division guards throughout.  Deterministic ordering.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

# Ordered list of (bare_config, plugin_config, display_name)
PAIRS = [
    ("bare",   "plugin",        "Opus 4.8"),
    ("sonnet", "sonnet-plugin", "Sonnet 4.6"),
    ("haiku",  "haiku-plugin",  "Haiku 4.5"),
    ("fable",  "fable-plugin",  "Fable 5"),
]


def load(path: Path) -> list[dict]:
    rows = list(csv.DictReader(path.open()))
    if not rows:
        sys.exit("error: empty results file")
    return rows


def agg(rows: list[dict]) -> dict:
    """Aggregate rows into {config: {category: {n, pass, cost_sum, cost_n, dur_sum}}}."""
    cells: dict = defaultdict(lambda: defaultdict(
        lambda: {"n": 0, "pass": 0, "cost_sum": 0.0, "cost_n": 0, "dur_sum": 0}
    ))
    for r in rows:
        config = r["config"]
        cat = r["category"]
        for key in [cat, "OVERALL"]:
            c = cells[config][key]
            c["n"] += 1
            c["pass"] += int(r["pass"])
            c["dur_sum"] += int(r["duration_s"])
            if r.get("cost_usd", "") not in ("NA", ""):
                c["cost_sum"] += float(r["cost_usd"])
                c["cost_n"] += 1
    return cells


def pass_rate(cell: dict) -> float | None:
    if not cell or cell["n"] == 0:
        return None
    return cell["pass"] / cell["n"]


def mean_cost(cell: dict) -> float | None:
    if not cell or cell["cost_n"] == 0:
        return None
    return cell["cost_sum"] / cell["cost_n"]


def mean_dur(cell: dict) -> float | None:
    if not cell or cell["n"] == 0:
        return None
    return cell["dur_sum"] / cell["n"]


def fmt_delta(base: float | None, new: float | None) -> str:
    """Return signed Δ% string.  Uses − (U+2212) for negative."""
    if base is None or new is None or base == 0:
        return "n/a"
    pct = (new - base) / base * 100
    sign = "+" if pct >= 0 else "−"
    return f"{sign}{abs(pct):.1f}%"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{round(value * 100)}%"


def print_pair(label: str, bare_cfg: str, plugin_cfg: str, cells: dict) -> None:
    bare  = cells.get(bare_cfg,   {})
    plugin = cells.get(plugin_cfg, {})

    b_all = bare.get("OVERALL",   {"n": 0, "pass": 0, "cost_sum": 0, "cost_n": 0, "dur_sum": 0})
    p_all = plugin.get("OVERALL", {"n": 0, "pass": 0, "cost_sum": 0, "cost_n": 0, "dur_sum": 0})

    b_pass = fmt_pct(pass_rate(b_all))
    p_pass = fmt_pct(pass_rate(p_all))
    cost_delta = fmt_delta(mean_cost(b_all), mean_cost(p_all))
    time_delta = fmt_delta(mean_dur(b_all), mean_dur(p_all))

    # Header
    print(f"\n## {label}\n")
    print(f"| Model | Success bare → +plugin | Cost/run bare → +plugin (Δ) | Time bare → +plugin (Δ) |")
    print(f"|---|---|---|---|")
    print(f"| OVERALL | {b_pass} → {p_pass} | {cost_delta} | {time_delta} |")

    # Per-category drill-down (only where success rate differs)
    all_cats = sorted(
        (k for k in set(bare.keys()) | set(plugin.keys()) if k != "OVERALL")
    )
    drill_rows = []
    for cat in all_cats:
        b_cell = bare.get(cat,   {"n": 0, "pass": 0, "cost_sum": 0, "cost_n": 0, "dur_sum": 0})
        p_cell = plugin.get(cat, {"n": 0, "pass": 0, "cost_sum": 0, "cost_n": 0, "dur_sum": 0})
        br = pass_rate(b_cell)
        pr = pass_rate(p_cell)
        if br is None or pr is None:
            continue
        if abs(br - pr) < 1e-9:   # same → skip
            continue
        b_pct = fmt_pct(br)
        p_pct = fmt_pct(pr)
        drill_rows.append((cat, b_pct, p_pct))

    if drill_rows:
        print()
        print("### Category drill-down (changed)\n")
        print("| Category | bare | +plugin |")
        print("|---|---|---|")
        for cat, b_pct, p_pct in drill_rows:
            print(f"| {cat} | {b_pct} | {p_pct} |")


def main() -> None:
    path = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).parent / "results/results-v0.2.0.csv"
    )
    rows = load(path)
    cells = agg(rows)

    present = {r["config"] for r in rows}

    any_printed = False
    for bare_cfg, plugin_cfg, label in PAIRS:
        if bare_cfg not in present or plugin_cfg not in present:
            continue   # skip gracefully when either side absent
        print_pair(label, bare_cfg, plugin_cfg, cells)
        any_printed = True

    if not any_printed:
        print("No complete pairs found in the CSV.")


if __name__ == "__main__":
    main()
