# Running the benchmark

Requirements: Claude Code CLI (`claude`), `jq`, Python 3.11+, pytest.

    bench/run.sh --config bare   --reps 3   # Opus 4.8, no plugin
    bench/run.sh --config plugin --reps 3   # Opus 4.8 + modelharness core
    bench/run.sh --config fable  --reps 3   # Fable 5 (API key, or subscription until 2026-06-22)
    python3 bench/report.py                 # aggregate into the README table
    python3 bench/lift.py                    # per-model harness lift
    python3 bench/stats.py                   # paired per-task deltas with 95% confidence intervals
    python3 bench/chart.py                   # regenerate assets/benchmark-chart.svg from the CSV

Approximate cost for a full 8-config × 3-rep capture, measured from our v0.2.1 run:
≈$46 (opus bare) + $39 (opus+plugin) + $92 (fable) + $88 (fable+plugin) + $21 (sonnet)
+ $20 (sonnet+plugin) + $12 (haiku) + $12 (haiku+plugin) ≈ $330 total API-equivalent
(subscription usage if run via a logged-in Claude Code). Note: two-phase continuity
tasks run two fresh sessions per rep, so they count double against per-task cost
estimates.
Notes:
- Runs are fully autonomous (`--dangerously-skip-permissions`) inside throwaway temp
  dirs; tasks are offline and stdlib-only.
- Grading is hidden and binary: `hidden/` is copied in only AFTER the agent finishes.
- `bench/scripts/selfcheck.sh --all` proves every task fails untouched and passes on
  its reference solution.
- The `plugin` config injects the identical core text via `--append-system-prompt`
  (headless equivalent of the SessionStart hook), with skills referenced by path.
