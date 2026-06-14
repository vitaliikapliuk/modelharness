`normalize_id` in `normalizer.py` violates its documented contract (see its docstring).
Fix `normalize_id` to match the docstring exactly, and update ALL code that depends on
the old (buggy) behavior so that the end-to-end behavior exercised by the visible tests
(`test_visible.py`) still passes. The workspace contains four modules
(`normalizer.py`, `ledger.py`, `matcher.py`, `report.py`) and `test_visible.py`.

Do not change the docstring of `normalize_id` and do not modify or weaken the visible
tests.

The fix means removing the compensating string-reversal workarounds entirely; the graded
solution must contain no string-reversal (`[::-1]` or `reversed(`) in `ledger.py` or
`matcher.py`.

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
