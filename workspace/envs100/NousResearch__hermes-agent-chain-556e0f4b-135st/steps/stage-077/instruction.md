**fix(cron): scale missed-job grace window with schedule frequency**

Replaces hardcoded 120s grace window with dynamic scaling: min(period/2, 2h), floored at 120s. Daily jobs get 2h grace, hourly gets 30m, 5-min gets 2.5m. Prevents silent job skips on brief gateway reconnects.

41 cron/jobs tests pass.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_jobs.py`