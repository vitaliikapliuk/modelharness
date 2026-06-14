This token-bucket rate limiter is letting clients burst far beyond the configured
capacity in production. Find and fix the bug in `limiter.py`. Keep the public API
(`allow()` returns bool; constructor signature unchanged). `test_limiter_basic.py`
must keep passing.

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
