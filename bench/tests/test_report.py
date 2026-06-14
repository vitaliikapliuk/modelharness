import subprocess, sys, textwrap
from pathlib import Path

FIXTURE = textwrap.dedent("""\
    timestamp,task,category,config,rep,pass,cost_usd,duration_s,num_turns,asked_question
    2026-06-15T10:00:00Z,bugfix-cache-ttl,bugfix,bare,1,1,0.50,120,14,0
    2026-06-15T10:05:00Z,bugfix-cache-ttl,bugfix,bare,2,0,0.40,100,12,0
    2026-06-15T10:10:00Z,bugfix-cache-ttl,bugfix,plugin,1,1,0.55,130,15,0
    2026-06-15T10:15:00Z,bugfix-cache-ttl,bugfix,plugin,2,1,0.60,140,16,0
    2026-06-15T10:20:00Z,bugfix-cache-ttl,bugfix,fable,1,1,1.20,200,10,0
    2026-06-15T10:25:00Z,bugfix-cache-ttl,bugfix,fable,2,1,1.10,190,9,0
""")

FIXTURE_BARE_SONNET = textwrap.dedent("""\
    timestamp,task,category,config,rep,pass,cost_usd,duration_s,num_turns,asked_question
    2026-06-15T10:00:00Z,bugfix-cache-ttl,bugfix,bare,1,1,0.50,120,14,0
    2026-06-15T10:05:00Z,bugfix-cache-ttl,bugfix,bare,2,0,0.40,100,12,0
    2026-06-15T10:10:00Z,bugfix-cache-ttl,bugfix,sonnet,1,1,0.20,90,10,0
    2026-06-15T10:15:00Z,bugfix-cache-ttl,bugfix,sonnet,2,0,0.15,80,9,0
""")


def test_report_aggregates_by_config_and_category(tmp_path: Path):
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE)
    out = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "report.py"), str(csv)],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "| bugfix " in out
    assert "50%" in out      # bare: 1/2
    assert "100%" in out     # plugin and fable: 2/2
    assert "$0.45" in out    # bare mean cost
    assert "OVERALL" in out


def test_report_renders_only_present_configs(tmp_path: Path):
    """CSV with only bare+sonnet rows renders exactly two config columns."""
    csv = tmp_path / "results.csv"
    csv.write_text(FIXTURE_BARE_SONNET)
    out = subprocess.run(
        [sys.executable, str(Path(__file__).parent.parent / "report.py"), str(csv)],
        capture_output=True, text=True, check=True,
    ).stdout
    header_line = [l for l in out.splitlines() if l.startswith("|")][0]
    # Exactly two config columns: "Opus 4.8" and "Sonnet 4.6"
    assert "Opus 4.8" in header_line
    assert "Sonnet 4.6" in header_line
    # Columns not in the CSV must not appear
    assert "Opus 4.8 + modelharness" not in header_line
    assert "Haiku" not in header_line
    assert "Fable" not in header_line
    # Count pipe-separated segments (header has: | Category | col1 | col2 |)
    cols = [c.strip() for c in header_line.split("|") if c.strip()]
    assert len(cols) == 3  # "Category" + "Opus 4.8" + "Sonnet 4.6"
