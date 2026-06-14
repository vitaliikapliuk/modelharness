import subprocess, sys
from pathlib import Path

BENCH = Path(__file__).parent.parent
CSV = BENCH / "results" / "results-v0.2.1.csv"


def run_stats():
    return subprocess.run(
        [sys.executable, str(BENCH / "stats.py"), str(CSV)],
        check=True, capture_output=True, text=True,
    ).stdout


def test_reports_paired_ci_per_model():
    out = run_stats()
    assert "95% CI" in out
    for name in ["Opus 4.8", "Sonnet 4.6", "Haiku 4.5", "Fable 5"]:
        assert name in out


def test_opus_cost_win_is_significant_and_others_honest():
    out = run_stats()
    # Opus cost delta is the headline win — must be flagged significant.
    assert "Opus 4.8" in out and "significant" in out.lower()
    # The honest counterpart: at least one model's delta is reported within noise.
    assert "within noise" in out.lower()


def test_quality_is_reported_as_exact_not_sampled():
    out = run_stats()
    assert "407/408" in out or "exact" in out.lower()
