Users of this in-memory TTL cache report two production issues: (1) values are
sometimes returned after their TTL has expired, and (2) memory usage grows without
bound even though entries expire. Find and fix the bugs in `cache.py`. Do not change
the public API (`set`, `get`, `size`). The existing test in `test_cache_basic.py`
must keep passing.

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
