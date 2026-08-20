**fix(gateway): cancel_background_tasks must drain late-arrivals**

## Summary
During gateway shutdown, a message arriving while `cancel_background_tasks` is mid-`await` could spawn a fresh `_process_message_background` task that gets added to `self._background_tasks` — and the subsequent `_background_tasks.clear()` dropped the reference, leaving the task running untracked against a disconnecting adapter.

## Fix
Wrap the cancel+gather in a bounded loop (`MAX_DRAIN_ROUNDS=5`). If new tasks appear during the `gather`, cancel them in the next round. The `.clear()` at the end is preserved as a safety net.

## Changes
- `gateway/platforms/base.py`: re-drain loop in `cancel_background_tasks`.
- `tests/gateway/test_cancel_background_drain.py`: 3 regression cases (drain late arrivals, no-op path, bounded loop).

## Validation
| | Before | After |
|---|---|---|
| Late arrival during gather | task reference dropped, task runs orphaned | task drained in next round |
| No tasks | no-op | no-op (unchanged) |
| Single task | cancels in one round | cancels in one round (unchanged) |

Regression-guard: `test_cancel_background_tasks_drains_late_arrivals` stashed-fix run FAILS with `Late-arrival M2 was NOT cancelled ... the task leaked`; re-applied it passes. Also re-ran 76 related gateway tests (shutdown, command-bypass, pending-drain, busy-session-ack, session-race-guard) — all pass.

## Audit follow-up
While working on this I verified three other MEDs from the original race audit were false positives — the check-and-set patterns had no `await` between the read and write, so they're atomic on single-threaded asyncio:
- busy-handler double-ack (`gateway/run.py:_handle_active_session_busy_message`) — 3 concurrent busy messages produced exactly 1 ack
- Discord `ExecApprovalView` double-resolve — 2 concurrent button clicks produced exactly 1 `resolve_gateway_approval` call
- Discord `UpdatePromptView` — same pattern

No code changes needed for those.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_cancel_background_drain.py`