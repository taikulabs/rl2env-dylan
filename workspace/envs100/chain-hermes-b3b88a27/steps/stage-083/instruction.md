**fix(gateway): close pending-drain and late-arrival races in base adapter**

## Summary
Two related concurrency bugs in `gateway/platforms/base.py:_process_message_background` are closed. Platform-inherited behavior, so all adapters (Telegram, Discord, Slack, WhatsApp, …) benefit.

## R5 (HIGH) — duplicate agent spawn on turn chain
The pending-drain path deleted `_active_sessions[session_key]` before awaiting `typing_task.cancel()` and the recursive `_process_message_background` call. During the typing_task await, a concurrent inbound message could pass the Level-1 guard (entry missing), set its own Event, and spawn a second `_process_message_background` for the same session_key. Result: two agents running simultaneously — duplicate responses, duplicate tool calls.

**Fix:** keep the `_active_sessions` entry populated and only `.clear()` the Event. The guard stays live so any concurrent inbound message takes the busy-handler path (queue + interrupt) as intended.

## R6 (MED-HIGH) — message dropped during finally cleanup
The `finally` block had two await points (`typing_task`, `stop_typing`) before the unconditional `del self._active_sessions[session_key]`. A message arriving in that window passed the guard, landed in `_pending_messages` via the busy-handler — and then the del removed the guard with the message still queued. Nothing drained it.

**Fix:** before deleting `_active_sessions` in finally, pop any late pending entry and spawn a drain task for it. Only delete `_active_sessions` when no pending is waiting.

## Changes
- `gateway/platforms/base.py`: R5 fix at the pending-drain block; R6 fix at the finally-cleanup block.
- `tests/gateway/test_pending_drain_race.py`: three regression cases.

## Validation
| | Before | After |
|---|---|---|
| M1 drain + concurrent M3 during typing-cancel await | two `_process_message_background` for same session | guard stays live, M3 takes busy-handler path |
| Message arrives during finally cleanup awaits | silently dropped | drain task spawned, message processed |
| Normal turn with no pending | `_active_sessions` cleaned up | same (regression guard) |

Regression-guard validated: against unpatched `base.py`, the two race tests fail exactly where the bugs manifest (duplicate-spawn guard loses identity; "LATE" not in processed). With the fix applied, 3/3 pass.

Targeted suite green: `test_pending_drain_race.py` 3/3, `test_command_bypass_active_session.py` 41/41, `test_busy_session_ack.py` 9/9, `test_session_race_guard.py` 14/14, `test_gateway_shutdown.py` 6/6, `test_safe_adapter_disconnect.py` 3/3 — 76 total.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_pending_drain_race.py`