**fix: prevent unwanted session auto-reset after graceful gateway restarts**

## Summary

When the gateway restarts gracefully (via `hermes update`, `hermes gateway restart`, `/restart`, systemd restart, etc.), users' sessions should **not** be auto-reset. Previously, `suspend_recently_active()` fired on every startup — including planned restarts — causing users to lose their conversation history unexpectedly.

### The bug (reported by user)

1. User is chatting with the bot on Telegram
2. Agent runs `hermes update` via terminal tool (or user runs `/update`)
3. Gateway restarts
4. On startup, `suspend_recently_active()` marks all sessions updated in the last 120 seconds as suspended
5. User sends their next message → session auto-resets → conversation history cleared
6. User gets an unwanted 'Session automatically reset' notification they never asked for

### The fix

- **On graceful shutdown** (`stop()`): write a `.clean_shutdown` marker file in HERMES_HOME
- **On startup** (`start()`): if the marker exists, skip `suspend_recently_active()` and delete the marker
- **After a crash** (no marker): suspension still fires as before — this is the original crash-recovery behavior from #7536

The marker approach is robust: graceful shutdowns always go through `stop()` where the marker is written. Crashes/kills skip `stop()`, so no marker exists and crash recovery proceeds normally.

### Why this is safe

`suspend_recently_active()` was designed for **crash recovery** — preventing stuck sessions that were mid-processing when the gateway died unexpectedly. Graceful shutdowns already drain active agents via `_drain_active_agents()`, so there are no stuck sessions to recover from.

## Changes

- `gateway/run.py`: Write `.clean_shutdown` marker in `stop()`, check for it in `start()` before calling `suspend_recently_active()`
- `tests/gateway/test_clean_shutdown_marker.py`: 7 new tests covering marker creation, suspension skip, and crash-recovery behavior