**fix(gateway): propagate user identity through process watcher pipeline & guard None user_id**

## Summary

Fixes the spurious "Hi~ I don't recognize you yet!" pairing messages that fire when background processes complete or when platform messages arrive without user identity.

**What this PR does:** Propagates `user_id`/`user_name` through the full process watcher chain (ContextVars → terminal tool → process registry → process watcher → synthetic SessionSource), and adds a belt-and-suspenders guard that silently drops messages with `user_id=None` instead of triggering the pairing flow.

## Root Cause

`_set_session_env()` exported platform, chat_id, chat_name, and thread_id to session ContextVars — but NOT user_id/user_name. When background processes completed, `_run_process_watcher()` rebuilt the SessionSource without user identity. While  added an `internal=True` bypass for the specific notify_on_complete path, the underlying identity gap remained:

- Garbage entries in pairing rate limiters (`discord:None`, `telegram:None`)
- "User None" in approval messages and logs
- Platform messages without `from_user` (Telegram service messages, channel forwards, anonymous admin actions) could still trigger false pairing

## Changes

| File | Change |
|------|--------|
| `gateway/session_context.py` | Add `_SESSION_USER_ID` / `_SESSION_USER_NAME` ContextVars + plumb through set/clear |
| `gateway/run.py` | Pass user identity in `_set_session_env()`; read it in `_run_process_watcher()`; add None user_id guard before pairing |
| `tools/process_registry.py` | Add `watcher_user_id`/`watcher_user_name` to ProcessSession + checkpoint serialization/recovery |
| `tools/terminal_tool.py` | Read user identity from session ContextVars, include in both watcher dict paths |

**+167 lines, 0 deletions** across 8 files (4 source, 4 test).

## Tests

- 85 targeted tests pass (session env, internal bypass + pairing, process registry checkpoints, notify_on_complete recovery)
- New tests: `test_notify_on_complete_preserves_user_identity`, `test_none_user_id_skips_pairing`, `test_none_user_id_does_not_generate_pairing_code`
- Existing tests updated to verify user_id/user_name in checkpoint persistence and recovery

## Attribution

Salvaged from:
- PR #7664 (kagura-agent) — ContextVar-based user identity propagation approach
- PR #6540 (MestreY0d4-Uninter) — comprehensive test patterns for watcher identity
- PR #7709 (guang384) — None user_id guard concept

, #6485, #7643
Relates to #6516

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_internal_event_bypass_pairing.py`
- `tests/gateway/test_session_env.py`
- `tests/tools/test_notify_on_complete.py`
- `tests/tools/test_process_registry.py`