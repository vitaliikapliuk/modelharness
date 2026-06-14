# Benchmark task format

Each task is a directory under `bench/tasks/<task-name>/`:

    <task-name>/
    ├── meta.json        # {"category": "bugfix|feature|refactor|longhorizon",
    │                    #  "timeout_seconds": 900, "max_turns": 80}
    ├── PROMPT.md        # the exact prompt given to the agent (the ONLY thing it sees
    │                    #  besides workspace/)
    ├── workspace/       # the repo state the agent starts in (copied to a temp dir)
    └── hidden/          # NEVER copied into the workspace before/during the run
        ├── grade.sh     # run with CWD=workspace copy AFTER the agent finishes;
        │                #  exit 0 = pass, non-zero = fail
        ├── tests/       # hidden test files grade.sh uses
        └── reference/   # reference solution files (for selfcheck only, proves the
                         #  task is solvable; never shown to the agent)

## Two-phase tasks

A task may set `"phases": 2` in meta.json (absent or `1` = ordinary single-phase,
behavior unchanged). A two-phase task adds a `PROMPT2.md` alongside `PROMPT.md`:

- Phase 1 runs `claude -p` with `PROMPT.md` in a fresh temp workspace, as usual.
- Phase 2 runs a SECOND `claude -p` with `PROMPT2.md` in the SAME workspace. A
  separate `claude -p` call is a fresh session: no conversation carryover, only the
  files left on disk survive. This is the cross-session memory/handoff test.
- `timeout_seconds` and `max_turns` apply PER PHASE. The 429 retry logic applies per
  phase independently. If phase 1 ends in a terminal (non-429) error, phase 2 is still
  attempted — the task tests recovery.
- cost/duration/turns are summed across both phases; still one CSV row per rep.
- The hidden copy and `grade.sh` run only after phase 2.

`PROMPT2.md` should state that this is a fresh session with no access to the prior
conversation, and ask the agent to complete the in-progress work on disk.

Rules:
- Binary grading only. grade.sh must be deterministic and offline.
- grade.sh MUST fail on the untouched workspace (otherwise the task tests nothing)
  and MUST pass when hidden/reference/* files are copied over the workspace
  (otherwise the task may be unsolvable). `bench/scripts/selfcheck.sh` enforces both.
- workspace/ must be self-contained: Python 3.11+ stdlib + pytest only.
- PROMPT.md must demand full autonomy and forbid asking questions.
