`next_monthly(day_of_month, after)` should return the next datetime.date strictly
after `after` that falls on `day_of_month`, clamping to the last day of the month
when the month is shorter (e.g. day 31 in February -> Feb 28/29). In production it
crashes or returns wrong dates near month/year boundaries. Fix `schedule.py`. Keep
the function signature. `test_schedule_basic.py` must keep passing.

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
