#!/usr/bin/env python3
"""Aggregate bench/results/results.csv into the README markdown table.

Usage: python3 bench/report.py [path/to/results.csv]
"""
import csv, sys
from collections import defaultdict
from pathlib import Path

CONFIGS_ORDER = ["bare", "plugin", "sonnet", "sonnet-plugin", "haiku", "haiku-plugin", "fable", "fable-plugin"]
LABELS = {
    "bare":          "Opus 4.8",
    "plugin":        "Opus 4.8 + modelharness",
    "sonnet":        "Sonnet 4.6",
    "sonnet-plugin": "Sonnet 4.6 + modelharness",
    "haiku":         "Haiku 4.5",
    "haiku-plugin":  "Haiku 4.5 + modelharness",
    "fable":         "Fable 5",
    "fable-plugin":  "Fable 5 + modelharness",
}


def load(path: Path):
    rows = list(csv.DictReader(path.open()))
    if not rows:
        sys.exit("empty results file")
    return rows


def agg(rows):
    """-> {(category, config): {"n", "pass", "cost_sum", "cost_n", "dur_sum"}}"""
    cells = defaultdict(lambda: {"n": 0, "pass": 0, "cost_sum": 0.0, "cost_n": 0, "dur_sum": 0})
    for r in rows:
        for key in [(r["category"], r["config"]), ("OVERALL", r["config"])]:
            c = cells[key]
            c["n"] += 1
            c["pass"] += int(r["pass"])
            c["dur_sum"] += int(r["duration_s"])
            if r["cost_usd"] not in ("NA", ""):
                c["cost_sum"] += float(r["cost_usd"])
                c["cost_n"] += 1
    return cells


def fmt(cells, category, config):
    c = cells.get((category, config))
    if not c or c["n"] == 0:
        return "—"
    rate = round(100 * c["pass"] / c["n"])
    cost = f"${c['cost_sum'] / c['cost_n']:.2f}" if c["cost_n"] else "n/a"
    dur = round(c["dur_sum"] / c["n"])
    return f"{rate}% · {cost} · {dur}s"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "results/results.csv"
    rows = load(path)
    cells = agg(rows)
    categories = sorted({r["category"] for r in rows}) + ["OVERALL"]

    present = {r["config"] for r in rows}
    configs = [c for c in CONFIGS_ORDER if c in present]

    print("| Category | " + " | ".join(LABELS[c] for c in configs) + " |")
    print("|---|" + "---|" * len(configs))
    for cat in categories:
        print(f"| {cat} | " + " | ".join(fmt(cells, cat, c) for c in configs) + " |")
    print("\nCell format: success rate · mean cost per run · mean wall-clock.")


if __name__ == "__main__":
    main()
