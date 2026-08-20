**fix(gateway): auto-resume sessions after drain-timeout restart**

## Summary
Sessions interrupted by a drain-timeout gateway restart now auto-resume on the same `session_key` instead of getting silently converted into a fresh session with a contradictory reset notice.

Implements the spec in #11852 (BrennerSpear) with the approved correction (reuse existing `.restart_failure_counts` stuck-loop counter from #7536 rather than adding a parallel counter).

Root cause: drain-timeout restart skipped `.clean_shutdown` → startup called `suspend_recently_active()` → `get_or_create_session()` saw `suspended=True` → spawned a new `session_id` with `auto_reset_reason="suspended"` — contradicting the banner's "send any message after restart to resume" promise.

## Changes
- `gateway/session.py`: `SessionEntry` gains `resume_pending` / `resume_reason` / `last_resume_marked_at` fields (with to_dict/from_dict). New `SessionStore.mark_resume_pending()` / `clear_resume_pending()`. `get_or_create_session()` returns the existing entry when `resume_pending=True` (`suspended` still wins). `suspend_recently_active()` skips `resume_pending` entries.
- `gateway/run.py`: drain-timeout branch in `_stop_impl()` marks active sessions `resume_pending` (reason `restart_timeout` vs `shutdown_timeout`) before `_interrupt_running_agents()`. `_run_agent()` injects a reason-aware restart-resume system note that subsumes the tool-tail auto-continue note. Successful-turn cleanup clears `resume_pending` alongside `_clear_restart_failure_count()`. Shutdown banner softened to "I'll try to resume where you left off" — honest about stuck-loop escalation.
- `tests/gateway/test_restart_resume_pending.py`: 29 new tests.

## Invariants preserved
- Repeated interrupted restarts still escalate to `suspended=True` via the existing `.restart_failure_counts` counter (threshold 3) — no parallel counter added.
- `/stop` still hard-suspends.
- Clean-drain shutdowns still write `.clean_shutdown` and run no suspension on next start.
- Idle/daily `session_reset` policy unchanged.
- The PR #9934 tool-tail auto-continue note still fires for non-resume-pending interrupted sessions (crashes, SIGTERM without drain, etc.).

## Validation
| Scenario | Before | After |
|---|---|---|
| Drain-timeout restart, same `session_key` next message | Fresh `session_id` + "Session automatically reset. Use /resume..." | Same `session_id`, transcript reloaded, reason-aware restart-resume system note |
| Interrupted transcript NOT ending on `tool` role | No resume hint to the model | Reason-aware system note still fires (resume_pending metadata-driven) |
| `/stop` → suspend | New `session_id` + suspended notice | Unchanged |
| 3× consecutive restart-interrupt on same session | Stuck-loop counter flips suspended=True, fresh session | Unchanged (suspended overrides resume_pending) |
| Clean drain completes in time | No marking, `.clean_shutdown` written | Unchanged |
| Successful resumed turn | — | Clears `resume_pending` + stuck-loop counter |

Test runs (targeted):
- `tests/gateway/test_restart_resume_pending.py` — 29 passed
- `tests/gateway/test_restart_drain.py` `test_gateway_shutdown.py` `test_clean_shutdown_marker.py` `test_auto_continue.py` `test_stuck_loop.py` `test_restart_notification.py` `test_session.py` — 141 passed
- All 8 session-related test files — 139 passed
- Full `tests/gateway/` — 3286 passed, 7 pre-existing unrelated failures (signal phone redaction, matrix E2EE `olm` module, telegram approval buttons — all exist on `origin/main` without these changes)

## Credit
Spec authored by @BrennerSpear in #11852. This PR implements that spec.

 (spec → implementation).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_restart_resume_pending.py`