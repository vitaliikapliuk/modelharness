---
name: memory-discipline
description: Use when recording lessons learned in a project, or when a project contains lessons/ or MEMORY.md — file-based memory format and read/write rules that measurably improve long-horizon performance.
---

# Memory Discipline

Fable 5 performs notably better when it can write learnings somewhere for future
reference. Give Opus the same surface and rules.

## Read rules
- At the start of non-trivial work, read `MEMORY.md` (index) if present, then any
  `lessons/*.md` whose one-line summary looks relevant.
- Memories reflect what was true when written — verify a referenced file/flag still
  exists before relying on it.

## Write rules
- One lesson per file in `lessons/`, kebab-case name, one-line summary on the first line.
- Record corrections from the user and confirmed working approaches alike — include WHY
  it mattered, not just what happened.
- Don't save what the repo already records (code structure, git history, README facts).
- Update an existing lesson rather than creating a near-duplicate; delete lessons that
  turn out to be wrong.
- After writing, add/refresh a one-line pointer in `MEMORY.md`.

## Format

    <!-- lessons/use-fake-clock-in-timer-tests.md -->
    Timer tests must inject a fake clock — real sleeps made CI flaky.

    Context: PR #42 reverted twice. `time.monotonic` is patched via the `clock`
    parameter; never call `time.sleep` in tests.
