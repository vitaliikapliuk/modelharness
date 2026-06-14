---
description: Extract a full task specification up front (goal, constraints, definition of done), then execute — the primary documented lever for Opus 4.8 long-horizon quality.
---

The user wants to start a substantial task. Do NOT start working yet.

1. Read their request: $ARGUMENTS (if empty, ask what they want to build).
2. Interview briefly — one question at a time, only for genuinely missing pieces:
   - Goal: what outcome, for whom, why now?
   - Constraints: stack, style, what must NOT change, performance/compat limits?
   - Definition of done: which binary checks prove completion (tests pass, command
     output, observable behavior)?
3. Restate the complete specification in one block and get a quick confirmation.
4. Execute the full task against that spec autonomously: follow the modelharness core
   (grounded progress, self-verification cadence, fresh-context verification before
   completion claims). Do not stop to ask about minor decisions — note them instead.
