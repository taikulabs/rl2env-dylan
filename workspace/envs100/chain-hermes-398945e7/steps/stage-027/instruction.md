**fix(gateway): enforce auth check in busy-session path to prevent unauthorized injection**

Salvage of #17816 by @Bartok9 onto current main.

.

## Summary

Adds the missing `_is_user_authorized()` gate at the top of `_handle_active_session_busy_message()`, closing a P0 authorization bypass in shared-thread contexts (Slack/Telegram/Discord with `thread_sessions_per_user=False`, the default).

## Root cause

The cold path (`_handle_message`) correctly calls `_is_user_authorized()` before creating a session, but the busy path — reached when an active session already exists — skipped the check entirely. Non-allowlisted users in the same thread as an authorized user could queue text into `_pending_messages`, trigger `agent.interrupt()` with their content, receive a public `⚡ Interrupting...` ack, and end up addressed by name in the LLM reply.

Bypass commands (`/stop`, `/new`, `/approve`, etc.) were already safe — they route through `_message_handler` which hits the cold-path auth gate. The gap was exactly the busy/interrupt fallthrough.

## Changes

- `gateway/run.py`: 16-line auth gate at the top of `_handle_active_session_busy_message` — log warning, return True (handled = silently dropped).
- `tests/gateway/test_busy_session_auth_bypass.py`: 4 new cases — unauthorized dropped, authorized still processed, unauthorized blocked during drain, unauthorized can't steer.

## Validation

| | Before | After |
|---|---|---|
| Intruder in shared thread | queued + interrupted + acked + addressed by name | dropped silently |
| Authorized user | processed normally | processed normally |
| Tests | 15/15 busy-ack pass | 19/19 pass (4 new + 15 existing) |

Also ran all adjacent gateway auth suites: 41/41 pass across `test_allowlist_startup_check`, `test_auth_fallback`, `test_discord_bot_auth_bypass`, `test_unauthorized_dm_behavior`.

E2E reproduced the bypass on main and confirmed the fix blocks it — intruder → no queue, no interrupt, no ack; authorized user → unchanged.

Credit to @Bartok9 for the report-to-fix workflow and test coverage.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_busy_session_auth_bypass.py`