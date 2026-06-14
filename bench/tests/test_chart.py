import subprocess, sys
from pathlib import Path

BENCH = Path(__file__).parent.parent
CSV = BENCH / "results" / "results-v0.2.1.csv"


def run_chart(tmp_path):
    out = tmp_path / "chart.svg"
    subprocess.run([sys.executable, str(BENCH / "chart.py"), str(CSV), str(out)], check=True)
    return out.read_text()


def test_chart_contains_all_model_pairs_newest_first(tmp_path):
    svg = run_chart(tmp_path)
    fable = svg.index("Fable 5")
    opus = svg.index("Opus 4.8")
    sonnet = svg.index("Sonnet 4.6")
    haiku = svg.index("Haiku 4.5")
    assert fable < opus < sonnet < haiku  # newest first, top to bottom


def test_chart_values_come_from_csv(tmp_path):
    svg = run_chart(tmp_path)
    for label in ["$1.80", "$1.73", "$0.89", "$0.77", "$0.41", "$0.40", "$0.24"]:
        assert label in svg, f"missing {label}"
    assert "(−14%)" in svg or "(-14%)" in svg
    assert "only 98% tests passed" in svg
    assert "100% tests passed" in svg
    assert "BIGGEST GAIN" in svg


def test_chart_has_dark_mode_and_legend(tmp_path):
    svg = run_chart(tmp_path)
    assert "prefers-color-scheme" in svg
    assert "without modelharness" in svg
    assert "with modelharness" in svg
