**fix: reap orphaned browser sessions on startup**

## Summary

When the Python process that created a browser session exits uncleanly (SIGKILL, crash, gateway restart via `hermes update`), the in-memory `_active_sessions` tracking is lost but the agent-browser node daemons and their Chromium child processes keep running indefinitely.

**Impact found on production:** 24 orphaned sessions accumulated over 9 days, spawning 140 processes (node + Chromium trees) consuming **7.6 GB of RAM**. Memory watchdog showed steady growth from 30% to 64% over 3 weeks, with these zombies as the primary cause.

## Changes

- Add `_reap_orphaned_browser_sessions()` to `tools/browser_tool.py`
  - Scans `/tmp/agent-browser-{h_*,cdp_*}/` socket dirs on cleanup thread startup
  - For each dir not tracked by `_active_sessions`, reads the daemon PID file
  - SIGTERMs alive daemons, cleans up stale dirs
  - Handles: dead PIDs, corrupt PID files, PermissionError, foreign processes
  - Runs once on thread startup (not every 30s) to avoid races
- Called at the beginning of `_browser_cleanup_thread_worker()` before the periodic loop
- 9 new tests covering all edge cases

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_browser_orphan_reaper.py`