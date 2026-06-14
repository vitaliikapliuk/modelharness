`app.py` mixes storage, business logic, and formatting in one module. Refactor it:
- Create `storage.py` with a `Storage` class owning ALL dictionary state and access.
- Create `service.py` with the business rules (validation, totals), using Storage.
- `app.py` keeps only the public functions as thin delegations (max 40 lines) and
  must not touch any dict state directly.
Behavior must not change: `test_app.py` must pass unmodified.

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
