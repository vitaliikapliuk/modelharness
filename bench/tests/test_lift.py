"""Tests for bench/lift.py – harness-lift paired comparison.

Fixture design (hand-computed):
  bare    (Opus 4.8):  tasks=[bugfix-a cat=bugfix, bugfix-b cat=feature]
                       pass=[1,0]=50%, cost=[0.50,0.40] avg=$0.45, dur=[120,100] avg=110s
  plugin  (Opus 4.8+): tasks=[bugfix-a cat=bugfix, bugfix-b cat=feature]
                       pass=[1,1]=100%, cost=[0.55,0.60] avg=$0.575, dur=[130,140] avg=135s
  haiku (Haiku 4.5):   tasks=[bugfix-a cat=bugfix pass=0, bugfix-b cat=continuity pass=1]
                       pass=[0,1]=50%, cost=[0.10,0.12] avg=$0.11, dur=[50,60] avg=55s
  haiku-plugin (4.5+): tasks=[bugfix-a cat=bugfix pass=1, bugfix-b cat=continuity pass=1]
                       pass=[1,1]=100%, cost=[0.11,0.13] avg=$0.12, dur=[55,65] avg=60s

Opus lift:
  pass:  50% → 100%
  cost Δ: (0.575-0.45)/0.45 = +27.8%
  time Δ: (135-110)/110     = +22.7%

Haiku lift:
  pass:  50% → 100%
  cost Δ: (0.12-0.11)/0.11 = +9.1%
  time Δ: (60-55)/55       = +9.1%

Category drill-down (only categories where success rate differs bare→plugin):
  Opus bugfix:      1/1=100% bare, 1/1=100% plugin  → same, no drill-down
  Opus feature:     0/1=0%   bare, 1/1=100% plugin  → differs → shown
  Haiku bugfix:     0/1=0%   haiku, 1/1=100% haiku-plugin → differs → shown
  Haiku continuity: 1/1=100% haiku, 1/1=100% haiku-plugin → same, no drill-down
"""
import subprocess, sys, textwrap
from pathlib import Path

LIFT_PY = Path(__file__).parent.parent / "lift.py"

FIXTURE_CSV = textwrap.dedent("""\
    timestamp,task,category,config,rep,pass,cost_usd,duration_s,num_turns,asked_question
    2026-06-01T00:00:00Z,bugfix-a,bugfix,bare,1,1,0.50,120,10,0
    2026-06-01T00:01:00Z,bugfix-b,feature,bare,1,0,0.40,100,10,0
    2026-06-01T00:02:00Z,bugfix-a,bugfix,plugin,1,1,0.55,130,10,0
    2026-06-01T00:03:00Z,bugfix-b,feature,plugin,1,1,0.60,140,10,0
    2026-06-01T00:04:00Z,bugfix-a,bugfix,haiku,1,0,0.10,50,10,0
    2026-06-01T00:05:00Z,bugfix-b,continuity,haiku,1,1,0.12,60,10,0
    2026-06-01T00:06:00Z,bugfix-a,bugfix,haiku-plugin,1,1,0.11,55,10,0
    2026-06-01T00:07:00Z,bugfix-b,continuity,haiku-plugin,1,1,0.13,65,10,0
""")


def run_lift(csv_path):
    """Run lift.py with the given CSV path, return stdout."""
    result = subprocess.run(
        [sys.executable, str(LIFT_PY), str(csv_path)],
        capture_output=True, text=True,
    )
    return result.stdout, result.stderr, result.returncode


def test_lift_shows_model_display_names(tmp_path):
    """Output must contain the human-readable model display names for present pairs."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    assert "Opus 4.8" in out, f"Expected 'Opus 4.8' in output:\n{out}"
    assert "Haiku 4.5" in out, f"Expected 'Haiku 4.5' in output:\n{out}"


def test_lift_overall_row_per_model(tmp_path):
    """Each model pair must produce an OVERALL row."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # There should be at least two OVERALL rows (one per model pair)
    overall_count = out.count("OVERALL")
    assert overall_count >= 2, (
        f"Expected at least 2 OVERALL rows, found {overall_count}:\n{out}"
    )


def test_lift_pass_rate_column(tmp_path):
    """Success column must show bare→plugin pass rate strings."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # Both Opus and Haiku: 50% → 100%
    assert "50%" in out, f"Expected '50%' in output:\n{out}"
    assert "100%" in out, f"Expected '100%' in output:\n{out}"


def test_lift_cost_delta_percentage_opus(tmp_path):
    """Opus cost delta: (0.575 - 0.45) / 0.45 = +27.8%."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # Accept +27.8% or +27.7% (rounding variation)
    assert ("+27.8%" in out or "+27.7%" in out), (
        f"Expected '+27.8%' (Opus cost delta) in output:\n{out}"
    )


def test_lift_time_delta_percentage_opus(tmp_path):
    """Opus time delta: (135 - 110) / 110 = +22.7%."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    assert "+22.7%" in out, f"Expected '+22.7%' (Opus time delta) in output:\n{out}"


def test_lift_cost_delta_percentage_haiku(tmp_path):
    """Haiku cost delta: (0.12 - 0.11) / 0.11 = +9.1%."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    assert "+9.1%" in out, f"Expected '+9.1%' (Haiku cost delta) in output:\n{out}"


def test_lift_time_delta_percentage_haiku(tmp_path):
    """Haiku time delta: (60 - 55) / 55 = +9.1%."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # Same +9.1% as cost delta for haiku; already tested in cost test but fine to re-assert
    assert "+9.1%" in out, f"Expected '+9.1%' (Haiku time delta) in output:\n{out}"


def test_lift_drilldown_shows_differing_categories(tmp_path):
    """Per-category drill-down must appear for categories where pass rate differs."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # Opus: feature category differs (0%→100%), bugfix does not (100%→100%)
    # haiku: bugfix category differs (0%→100%), continuity does not (100%→100%)
    assert "feature" in out, f"Expected 'feature' category in drill-down:\n{out}"
    assert "bugfix" in out, f"Expected 'bugfix' category in drill-down:\n{out}"


def test_lift_drilldown_omits_same_categories(tmp_path):
    """Categories with identical pass rates between bare and plugin must not appear in drill-down."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # continuity: haiku=100%, haiku-plugin=100% → must NOT appear as a drill-down for Haiku
    # (it may appear in the main table OVERALL section only)
    # We check that if continuity appears, it's NOT in a "Haiku" drill-down section
    # Simplest proxy: the Haiku drill-down should NOT list continuity as a changed category
    lines = out.splitlines()
    in_haiku_section = False
    haiku_drilldown_lines = []
    for line in lines:
        if "Haiku 4.5" in line:
            in_haiku_section = True
        elif in_haiku_section and line.startswith("#"):
            # New top-level section for another model
            in_haiku_section = False
        if in_haiku_section:
            haiku_drilldown_lines.append(line)
    haiku_section_text = "\n".join(haiku_drilldown_lines)
    assert "continuity" not in haiku_section_text, (
        f"'continuity' should not appear in Haiku drill-down (rates equal):\n{haiku_section_text}"
    )


def test_lift_skips_absent_pair_gracefully(tmp_path):
    """When fable-plugin is absent, fable pair must be silently skipped (no crash, no fable section)."""
    # FIXTURE_CSV has no fable or fable-plugin rows
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    assert "Fable 5" not in out, f"'Fable 5' should not appear when pair is absent:\n{out}"


def test_lift_sonnet_absent_skipped(tmp_path):
    """When sonnet configs are absent, Sonnet 4.6 pair must not appear."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_CSV)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    assert "Sonnet 4.6" not in out, f"'Sonnet 4.6' should not appear when absent:\n{out}"


def test_lift_negative_delta_formatted_correctly(tmp_path):
    """When plugin is cheaper/faster, delta must be formatted as e.g. −13.5%."""
    fixture_negative = textwrap.dedent("""\
        timestamp,task,category,config,rep,pass,cost_usd,duration_s,num_turns,asked_question
        2026-06-01T00:00:00Z,task-a,bugfix,bare,1,1,0.50,120,10,0
        2026-06-01T00:01:00Z,task-a,bugfix,plugin,1,1,0.40,100,10,0
    """)
    csv = tmp_path / "results.csv"
    csv.write_text(fixture_negative)
    out, err, code = run_lift(csv)
    assert code == 0, f"lift.py exited {code}\nstderr: {err}\nstdout: {out}"
    # cost delta: (0.40-0.50)/0.50 = -20.0%
    assert "−20.0%" in out or "-20.0%" in out, (
        f"Expected '−20.0%' or '-20.0%' for negative delta:\n{out}"
    )
