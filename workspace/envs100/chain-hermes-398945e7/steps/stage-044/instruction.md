**fix(tui): return JSON-RPC errors for invalid request shapes**

Salvages #18054 onto current main. Authorship preserved via cherry-pick.

## Summary
TUI JSON-RPC dispatcher now returns structured errors for malformed input instead of crashing the `tui_gateway` subprocess with `AttributeError` on non-dict requests or list-valued `params`.

## Changes
- `tui_gateway/server.py`: adds `_normalize_request()` called from both `handle_request()` and `dispatch()`. Returns `-32600` for non-object requests and `-32602` for non-object `params`.
- 2 regression tests in `tests/test_tui_gateway_server.py`.

## Validation
- `scripts/run_tests.sh tests/test_tui_gateway_server.py` → 157/157 passing.

Credit: @Yukipukii1 (original PR #18054)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_tui_gateway_server.py`