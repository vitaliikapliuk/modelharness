# Contributing

Two highest-value contributions:

1. **Benchmark tasks.** Follow `bench/TASK_FORMAT.md`. Your PR must pass
   `bench/scripts/selfcheck.sh <your-task>` (fails untouched, passes on reference).
   Realistic > clever: tasks should look like actual work, not puzzles.
2. **Core improvements.** Any change to `core/modelharness-core.md` must (a) stay within
   the token budget (`scripts/check-core-budget.sh`) and (b) come with before/after
   numbers from at least `bench/run.sh --config plugin --reps 3` on the affected
   task categories.

All repo content is English-only. Run `scripts/smoke-hook.sh` before submitting
plugin changes.
