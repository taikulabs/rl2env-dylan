**fix: prevent duplicate completion notifications on process kill**

## Summary

When a background process with `notify_on_complete=True` is killed via `process(action="kill")`, two `[SYSTEM: Background process ... completed]` messages are delivered to the agent instead of one.

### Root cause

Race condition between `kill_process()` and the reader thread:

1. `kill_process()` sends SIGTERM → sets `exit_code = -15` → calls `_move_to_finished()` → enqueues notification
2. Reader thread's `process.wait()` returns → sets `exit_code = 143` (128+SIGTERM) → calls `_move_to_finished()` → enqueues **second** notification

### Fix

Make `_move_to_finished()` idempotent: track whether the session was actually removed from `_running`. On the second call, `_running.pop()` returns `None` (already moved), so the completion notification is skipped.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_notify_on_complete.py`