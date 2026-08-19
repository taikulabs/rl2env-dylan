**fix(gateway): merge rapid TEXT follow-ups during active sessions**

## Summary
Rapid TEXT follow-ups while the agent is running now accumulate instead of clobbering each other. Three quick messages "A", "B", "C" all reach the next turn as `A\nB\nC` — previously only "C" survived.

**Root cause:** `gateway/platforms/base.py` active-session branch stored the pending event as a single-slot replacement (`self._pending_messages[session_key] = event`). Message B overwrote A before the consumer read it; C overwrote B. Issue #4469's exact symptom.

**Fix:** Route the follow-up through `merge_pending_message_event(..., merge_text=True)` — the same helper that already merges photo bursts, and the same path the Telegram bursty-grace branch in `gateway/run.py` already uses for text.

## Changes
- `gateway/platforms/base.py`: 1-call swap (single-slot assign → merge call) with a comment block explaining the prior behavior and why `merge_text=True` matches the Telegram grace path.
- `tests/gateway/test_active_session_text_merge.py`: new regression test — three rapid TEXT events through `BasePlatformAdapter.handle_message` with an active session, asserts the pending slot holds `"part two\npart three"` and the interrupt event fires.

## Validation
| | Before fix | After fix |
|---|---|---|
| 3 rapid TEXT messages | only last survives | all accumulated |
| New regression test | fails (`'part three'`) | passes |
| `tests/gateway/test_session_race_guard.py` etc. (114 related tests) | n/a | 114 passed |
| Full `tests/gateway/` | n/a | 5441 passed, 7 skipped, 1 pre-existing flake (`test_blocking_approval_approve_once` — passes in isolation and on clean main) |

## Related
. PR #4491 attempted the same fix but against a 5000+ commit stale codebase against `GatewayRunner._pending_messages` (now dead state on main); credit @devorun for the original investigation and queue-disconnect analysis that surfaced the underlying handling.