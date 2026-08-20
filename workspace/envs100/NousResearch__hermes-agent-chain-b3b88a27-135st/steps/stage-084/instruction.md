**fix(tui): reject history-mutating commands while session is running**

## Summary
Fixes silent data loss in the TUI when `/undo`, `/compress`, `/retry`, or `rollback.restore` runs during an in-flight agent turn. The version-guard at `prompt.submit` would fail the version check and silently skip writing the agent's result — UI showed the assistant reply but the DB / backend history never received it, causing UI↔backend desync that persisted across session resume.

## Root cause
`prompt.submit` snapshots `history_version` at start, runs the agent, then writes the result list back only when the version still matches. If `/undo` / `/compress` / `/retry` / `rollback.restore` bumped the version mid-run, the write was silently skipped. The UI still received `message.complete`, so from the user's perspective the reply landed — except it didn't, and the next session resume was missing it.

## Changes
- `tui_gateway/server.py`:
  - `session.undo`, `session.compress`, `/retry`, `rollback.restore` (full-history only — file-scoped rollbacks still allowed): reject with code 4009 when `session.running` is True. Users can `/interrupt` first.
  - `prompt.submit`: on history_version mismatch (defensive backstop), attach a `warning` field to `message.complete` and log to stderr, instead of silently dropping the agent's output. UIs can surface the warning; operators see the mismatch in logs.
- `tests/test_tui_gateway_server.py`: 6 new regression cases.

## Validation
| | Before | After |
|---|---|---|
| `/undo` mid-turn | silently drops agent output; desync | 4009 rejected; agent keeps running |
| `/compress` mid-turn | same | 4009 rejected |
| `/retry` mid-turn | same | 4009 rejected |
| Full-history `rollback.restore` mid-turn | same | 4009 rejected |
| File-scoped `rollback.restore` mid-turn | allowed | still allowed (disk only, safe) |
| Any path that still bumps version mid-turn | silent drop | `warning` in `message.complete` payload + stderr log |
| All the above while idle | works | works (regression guard) |

Regression-guard validated: against unpatched `server.py`, 3 of the new tests fail exactly where the bugs manifest (undo/compress/version-mismatch). With the fix, all 6 pass.

Targeted: `test_tui_gateway_server.py` 33/33, plus `tui_gateway/` subtree 74/74.

Live E2E against the live Python environment:
```
=== Patch verification ===
  undo guard: OK
  compress guard: OK
  retry guard: OK
  rollback guard: OK
  backstop warning: OK

=== E2E scenarios ===
  undo (running=True):     error_code=4009  hist_len=2 (unchanged)
  compress (running=True): error_code=4009
  rollback-full (running): error_code=4009
  rollback-file (running): error_code=5021 (guard didn't block; file-scoped allowed)
  undo (running=False):    result={'removed': 2}  hist_len=0
```

## Not in scope
- UI-side rendering of the new `warning` field in `message.complete` — can be a small follow-up in `ui-tui/src/app/createGatewayEventHandler.ts`. For now the backstop writes to stderr which operators can inspect.
- The other two TUI HIGH finds (cross-session `_pending` blast, single-threaded RPC dispatch) remain open.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_tui_gateway_server.py`