**fix(cron): mark session as ended after job completes**

## Summary

Salvage of PR #2979 by @ygd58. .

Cron was the only execution path that never called `end_session()`, leaving `ended_at = NULL` permanently. This made cron sessions invisible to `hermes prune --older-than` and indistinguishable from active sessions.

## Bug in original PR

The original PR called `_session_db.end_session()` with zero arguments, but the method requires `(session_id, end_reason)`. This would have been a silent `TypeError` at runtime (swallowed by the `except Exception` wrapper), so sessions still wouldn't get marked.

## Fix

- Captured session_id in `_cron_session_id` before agent construction so it's available in the `finally` block even if `AIAgent()` fails
- Calls `end_session(_cron_session_id, 'cron_complete')` with proper arguments
- Updated existing test to verify `end_session` is called with correct args

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`