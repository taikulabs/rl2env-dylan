**fix(gateway): bypass active-session guard for gateway-handled slash commands**

## Summary
/help, /commands, /profile, and /update no longer silently vanish when sent during an active agent turn — they now dispatch inline instead of being queued and discarded by the pending-command safety net.

Salvaged from #11310 (by @Xowiek) onto current main. During conflict resolution the bypass set picked up `agents` (added to main in 99fd3b51 after the PR branched) so /agents and /tasks continue to bypass alongside the four newly-added commands.

## Changes
- `hermes_cli/commands.py`: new `ACTIVE_SESSION_BYPASS_COMMANDS` frozenset + `should_bypass_active_session()` helper, with alias canonicalization via `resolve_command()`
- `gateway/platforms/base.py`: Level-1 adapter guard now uses the helper instead of a hardcoded tuple
- `gateway/run.py`: Level-2 runner fast path directly dispatches /help, /commands, /profile, /update when the agent is running
- Regression tests for adapter-level (/help, /update) and runner-level (/help, /commands, /profile, /update) dispatch

## Validation
| | Before | After |
|---|---|---|
| /help during active turn | queued → dropped by safety net, no response | dispatched inline, user sees help |
| /commands during active turn | queued → dropped, no response | dispatched inline |
| /profile during active turn | queued → dropped, no response | dispatched inline |
| /update during active turn | queued → dropped, no response | dispatched inline |
| /agents, /tasks during active turn | bypassed (hardcoded) | bypassed (frozenset + alias resolution) |
| /stop, /new, /approve, /deny, etc. | bypassed (hardcoded) | bypassed (frozenset) |

Targeted tests: `tests/gateway/test_command_bypass_active_session.py` + `test_session_race_guard.py` → 39/39 pass.

Live E2E (adapter `handle_message` with active session): 16 bypass commands dispatch inline, 3 non-bypass cases (/model, plain text, /nonexistent) correctly don't.

.