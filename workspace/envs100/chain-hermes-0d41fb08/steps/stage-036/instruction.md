**fix(agent): catch PermissionError in subdirectory hint discovery**

## Summary

Wraps unguarded `Path.is_dir()` and `Path.is_file()` calls in `agent/subdirectory_hints.py` with `try/except OSError` so that inaccessible directories (e.g. `/root` from a non-root Daytona user) don't crash the agent.

## Changes

- **`_is_valid_subdir()`** — wrap `path.is_dir()` in `try/except OSError`
- **`_load_hints_for_directory()`** — wrap `hint_path.is_file()` in `try/except OSError`
- **Tests** — 3 new regression tests covering PermissionError in both methods and end-to-end via `check_tool_call()`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_subdirectory_hints.py`