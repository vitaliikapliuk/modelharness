#!/usr/bin/env python3
"""Render the hero benchmark chart (paired bars per model) as SVG, from the CSV.

Usage: python3 bench/chart.py [results.csv] [out.svg]
Defaults: bench/results/results-v0.2.1.csv -> assets/benchmark-chart.svg
"""
import csv
import sys
from pathlib import Path

# (display name, release tag, bare config, plugin config) — newest first
PAIRS = [
    ("Fable 5", "Jun 2026", "fable", "fable-plugin"),
    ("Opus 4.8", "2026", "bare", "plugin"),
    ("Sonnet 4.6", "Nov 2025", "sonnet", "sonnet-plugin"),
    ("Haiku 4.5", "Oct 2025", "haiku", "haiku-plugin"),
]

W, BAR_H, GAP, GROUP_GAP, LEFT, RIGHT, TOP = 760, 16, 4, 26, 10, 230, 64
GRAY, GREEN, RED = "#d0d7de", "#2da44e", "#d1737a"


def load_means(path):
    cost, passed, n = {}, {}, {}
    for r in csv.DictReader(open(path)):
        c = r["config"]
        cost[c] = cost.get(c, 0.0) + float(r["cost_usd"])
        passed[c] = passed.get(c, 0) + int(r["pass"])
        n[c] = n.get(c, 0) + 1
    return ({c: cost[c] / n[c] for c in cost},
            {c: 100.0 * passed[c] / n[c] for c in passed})


def fmt_delta(bare, mh):
    d = (mh / bare - 1) * 100
    return f"(−{abs(d):.0f}%)" if round(d) <= -1 else f"(−{abs(d):.1f}%)"


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "results/results-v0.2.1.csv"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "assets/benchmark-chart.svg"
    cost, passrate = load_means(src)
    maxv = max(cost.values())
    bar_w = W - LEFT - RIGHT

    rows, y = [], TOP
    for name, rel, bare, mh in PAIRS:
        star = ('  <g transform="translate(%d,%d)"><rect width="92" height="14" rx="7" fill="#bf8700"/>'
                '<text x="46" y="10.5" font-size="9" font-weight="bold" fill="#fff" text-anchor="middle">'
                '★ BIGGEST GAIN</text></g>' % (LEFT + len(name) * 8 + 60, y - 12)) if bare == "bare" else ""
        rows.append(f'  <text x="{LEFT}" y="{y}" class="t" font-size="13" font-weight="bold">{name} '
                    f'<tspan class="dim" font-weight="normal">({rel})</tspan></text>{star}')
        y += 6
        for cfg, color in ((bare, GRAY), (mh, GREEN)):
            w = bar_w * cost[cfg] / maxv
            label = f"${cost[cfg]:.2f}"
            if cfg == mh:
                if passrate[bare] < 100:
                    label += f' · 100% tests passed'
                elif cost[mh] < cost[bare]:
                    label += f" {fmt_delta(cost[bare], cost[mh])}"
            elif passrate[cfg] < 100:
                label += f" · only {passrate[cfg]:.0f}% tests passed"
            lcolor = (GREEN if cfg == mh and (cost[mh] < cost[bare] or passrate[bare] < 100)
                      else RED if passrate[cfg] < 100 else "currentColor")
            rows.append(f'  <rect x="{LEFT}" y="{y}" width="{w:.0f}" height="{BAR_H}" rx="3" fill="{color}"/>')
            rows.append(f'  <text x="{LEFT + w + 8:.0f}" y="{y + 12}" class="t" font-size="12" fill="{lcolor}">{label}</text>')
            y += BAR_H + GAP
        y += GROUP_GAP
    height = y + 6

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Cost per task with and without modelharness, per model">
<style>
  .t {{ font-family: -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; fill: #1f2328; }}
  .dim {{ fill: #8b949e; }}
  @media (prefers-color-scheme: dark) {{ .t {{ fill: #e6edf3; }} }}
</style>
<text x="{LEFT}" y="20" class="t" font-size="15" font-weight="bold">Cost per task, $ — same 17-task benchmark</text>
<rect x="{LEFT}" y="32" width="10" height="10" rx="2" fill="{GRAY}"/><text x="{LEFT + 16}" y="41" class="t" font-size="11">without modelharness</text>
<rect x="{LEFT + 160}" y="32" width="10" height="10" rx="2" fill="{GREEN}"/><text x="{LEFT + 176}" y="41" class="t" font-size="11">with modelharness</text>
{chr(10).join(rows)}
</svg>
'''
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
