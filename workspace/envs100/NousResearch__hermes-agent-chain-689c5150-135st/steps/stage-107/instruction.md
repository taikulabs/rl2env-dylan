**fix: prevent stale os.environ leak after clear_session_vars**

## Summary

 — After `clear_session_vars()` reset contextvars, `get_session_env()` fell back to `os.environ`, resurrecting stale `HERMES_SESSION_*` values from previous sessions. This broke session isolation in the gateway.

## Root Cause

The contextvars had `default=""`. After `clear_session_vars()` called `var.reset(token)` (restoring to default), `get_session_env()` checked `if value:` — empty string is falsy → fell through to `os.environ`. "Explicitly cleared" was indistinguishable from "never set."

## Fix

Use a sentinel (`_UNSET = object()`) as the contextvar default. Three states are now cleanly separated:

| State | `var.get()` | `get_session_env()` behavior |
|-------|------------|-------------------------------|
| Never set (CLI/cron) | `_UNSET` | Falls back to `os.environ` ✓ |
| Explicitly cleared | `""` | Returns `""` — no fallback ✓ |
| Actively set | `"telegram"` | Returns the value ✓ |

`clear_session_vars()` now uses `var.set("")` instead of `var.reset(token)` to mark the "explicitly cleared" state.

## Tests

- 9 existing session_env tests pass (3 updated to match new correct behavior)
- Added autouse fixture to reset contextvars between tests (test isolation)
- E2E verified: set → clear → no os.environ leak, CLI fallback still works

## Related PRs

Supersedes #10407, #10352 which targeted the same issue.