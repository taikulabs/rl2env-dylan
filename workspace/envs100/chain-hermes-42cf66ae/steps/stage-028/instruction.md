**fix(cron): persist cron sessions to SQLite**

## Summary
- 
- tag persisted cron-run sessions with `source=cron` instead of falling back to `cli`
- close the per-run SessionDB and add regression coverage for cron session wiring

## Contributor credit
- 
- added a small follow-up commit for cron source tagging and tests

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`