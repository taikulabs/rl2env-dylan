**fix(tui): session.create build thread must clean up if session.close races**

## Summary
Fast `/new` or `/resume` churn no longer leaks slash_worker subprocesses or approval-notify registrations. Previously, if `session.close` ran while the previous `session.create`'s `_build` thread was still mid-agent-init, `close` couldn't see the worker/notify `_build` was about to install — so they leaked onto an orphaned session dict until process exit.

## Race scenario
1. User runs `/new` (first time). `session.create` spawns `_build` thread, returns sid synchronously.
2. `_build` blocks in `_make_agent` (credential probe, client build — takes 2–3s).
3. User hits `/new` again before step 2 completes. Ink calls `closeSession(old_sid)` then `session.create` for the new one.
4. `session.close` pops `_sessions[old_sid]`, sees `slash_worker=None` (not yet installed), returns cleanly.
5. `_build` finishes, installs `slash_worker = _SlashWorker(...)` and `register_gateway_notify(key)` on the orphaned session dict.
6. Resources leak: subprocess runs until atexit, notify callback lingers in the global registry.

## Fix
`_build` now tracks what it allocates (`worker`, `notify_registered`). Its `finally` block checks whether `_sessions[sid]` still points to the session it was building for. If not, it was orphaned by a racing `close` — close the subprocess and unregister the notify itself.

## Changes
- `tui_gateway/server.py`: `_build` now reads `_sessions.get(sid)` safely, tracks allocations, and cleans up in `finally` on orphan detection.
- `tests/test_tui_gateway_server.py`: 2 regression cases.

## Validation
| | Before | After |
|---|---|---|
| `/new` during in-progress agent init | subprocess leaks, notify lingers | subprocess closed, notify unregistered |
| `/new` with no race (happy path) | works | works — no over-eager cleanup |

Regression-guard: against the unpatched code, the race test fails with `orphan worker was not cleaned up — closed_workers=[]`. With the fix the worker is cleaned up exactly once.

Targeted: `test_tui_gateway_server.py` 43/43, `tests/tui_gateway/` 41/41 — 84 total.

Live E2E against the live Python environment:
```
=== Race scenario ===
  session.create → sid=97a84e0d
  session.close → closed=True
  closed_workers after close (should be 0): 0
  closed_workers after build finish (should be 1): 1
  unregistered entries (should be >=1): 2

  Orphan cleanup: OK
```