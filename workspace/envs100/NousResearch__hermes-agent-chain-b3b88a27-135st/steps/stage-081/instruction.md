**fix(gateway): mark only still-running sessions resume_pending on drain timeout**

## Summary
 — the drain-timeout branch now marks only sessions that are still blocking the shutdown, not every session that was active when the drain started.

The original landing used `active_agents.keys()` (the drain-start snapshot) when marking `resume_pending`. That snapshot includes sessions that finished gracefully during the drain window. Marking them would give their next turn a stray "your previous turn was interrupted by a gateway restart" system note even though the prior turn actually completed cleanly.

## Changes
- `gateway/run.py`: swap `active_agents.keys()` for filtered `self._running_agents.items()` iteration in the drain-timeout mark loop. Mirrors `_interrupt_running_agents()` exactly — same set, same pending-sentinel skip.
- `tests/gateway/test_restart_resume_pending.py`: two regression tests.

## Validation
| Scenario | Before | After |
|---|---|---|
| Session finishes during drain window | Marked `resume_pending`; next turn gets a false interruption note | Not marked; normal fresh turn |
| Session still running at drain timeout | Marked | Marked (unchanged) |
| Pending sentinel (agent not constructed yet) in `_running_agents` | Marked | Skipped — mirrors `_interrupt_running_agents` behaviour |

Targeted test runs:
- `tests/gateway/test_restart_resume_pending.py` `test_gateway_shutdown.py` `test_restart_drain.py` `test_clean_shutdown_marker.py` — 57 passed (31 in resume_pending suite, up from 29 with the two new regression tests).