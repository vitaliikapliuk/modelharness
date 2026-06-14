The three handlers in `handlers.py` copy-paste the same validation and lookup block.
Refactor so the shared logic exists EXACTLY ONCE (a helper function or class), with
the three handlers reduced to their unique parts. Behavior must not change:
`test_handlers.py` must pass unmodified. The literal marker comment
"# shared-validation-block" currently appears 3 times; after your refactor it must
appear at most once (keep it on the shared helper).

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
