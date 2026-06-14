---
description: Spawn a fresh-context verifier subagent to check completed work against its specification before trusting it.
---

Verify the most recent substantial piece of work in this session (or, if
$ARGUMENTS names a scope, verify that instead).

1. Collect: the original specification / request, the definition-of-done checks, and
   the current state (run `git diff` / `git status` if the work is in a repo;
   otherwise list the produced artifacts).
2. Dispatch the `modelharness:verifier` agent with all of the above. Ask it to verify
   independently — run the checks itself, not trust your summary.
3. Report its verdict to the user verbatim in structure: confirmed / gaps found /
   not verifiable. If gaps were found, propose fixes but do not apply them without
   the user's go-ahead unless the session was already running autonomously.
