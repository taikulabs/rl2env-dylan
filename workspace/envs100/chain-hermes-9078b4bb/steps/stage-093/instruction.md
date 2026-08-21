**fix(tui): preserve live session identity across compression**

## Summary

 — TUI auto-compression can fork live session lineage and mix messages across sessions.

When a session rotates id on compression, `_sync_session_key_after_compress()` (`tui_gateway/server.py`) re-anchors the session_key, approval-notify routing, yolo state, and slash worker — but **never moves the active-session lease**, which stays keyed to the pre-compression id. And `_find_live_session_by_key()` matches live sessions on the stale `session_key`, not the live agent's current `agent.session_id`. After compression, a resume/create path fails to recognize the existing live agent and can build a **second live agent against the same DB continuation** → forked lineage / cross-session message mixing.

Verified still live on current `main` (`64131bf97`): `active_sessions.py` has only `release_active_session` (no transfer); the lease and lookup gaps are unfixed. The PR's 3 regression tests fail on bare main with the exact symptoms (`transfer_active_session` missing; `lease.session_id == 'session-old'` instead of `'session-new'`).

## Fix

- `active_sessions.transfer_active_session()` — move a lease in place to the new id (no slot drop);
- gateway `_transfer_active_session_slot()` (release+reacquire fallback) called inside `_sync_session_key_after_compress()`;
- `_session_lookup_key()` makes live-session lookup authoritative on `agent.session_id`, wired into **all** stale-`session_key` consumers (`_find_live_session_by_key`, `_session_live_item`, `_live_session_payload`) — fixes the whole lookup class.

## Salvage / attribution

Salvaged from #49086 (@konsisumer), cherry-picked onto current `main`; authored by @konsisumer. Applies cleanly (no conflicts).

## Tests

3 new regression tests (lease/session_id-agreement behavior contracts). 74 pass across `tests/tui_gateway/test_protocol.py` + `tests/hermes_cli/test_active_sessions.py`; all 3 fail on bare main (bug proven).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_active_sessions.py`
- `tests/tui_gateway/test_protocol.py`