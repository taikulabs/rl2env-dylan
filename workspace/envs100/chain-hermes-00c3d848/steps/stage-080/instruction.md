**fix(tui): keep /title session names in sync**

## Summary
- route TUI `/title` through the dedicated `session.title` RPC instead of the detached slash worker, so title updates always target the live TUI session
- queue title updates in `tui_gateway` when the session DB row is not ready yet, then apply them once session initialization creates the row
- add regression tests for queued/persisted title behavior and local slash handling

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_tui_gateway_server.py`
- `tests/tools/test_dockerfile_pid1_reaping.py`
- `ui-tui/src/__tests__/createSlashHandler.test.ts`