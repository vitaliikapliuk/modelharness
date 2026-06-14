---
name: verification-loop
description: Use when a task spans more than a few steps or files — establishes a checkable definition of done, a verification cadence, and fresh-context verifier subagents before claiming completion.
---

# Verification Loop

Fable 5 builds its own checking harness on long tasks. Reproduce that explicitly.

## 1. Define "done" before starting
Write down (in your todo list or a scratch note) the binary checks that prove the task
is complete: which tests must pass, which command must produce which output, which
behavior must be observable. If the user's request doesn't define them, derive them
and state them in one sentence.

## 2. Verify on a cadence, not at the end
After each meaningful increment (a function implemented, a module refactored), run the
relevant real check immediately — the actual test command, the actual build. Never
batch all verification to the end of a long task; errors compound.

## 3. Fresh-context verification before completion claims
Before declaring a substantial task complete, dispatch a verifier subagent
(`modelharness:verifier` agent, or a general-purpose subagent given the
`agents/verifier.md` instructions). Give it: the original specification, the
definition-of-done checks, and the current diff (`git diff` output or changed file
list). A fresh context catches what you have rationalized away. Self-review is the
fallback only when subagents are unavailable.

## 4. Act on the verdict
If the verifier reports gaps: fix them, re-run the checks, re-verify. Only report
completion to the user when checks pass AND the verifier (or the checks themselves)
confirm it. Report any unverified remainder explicitly.
