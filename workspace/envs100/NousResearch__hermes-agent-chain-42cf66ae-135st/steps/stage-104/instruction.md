**fix(cli): accept session ID prefixes for session actions**

## Summary
- resolve session IDs by exact match or unique prefix for `hermes sessions delete`, `export`, and `rename`
- make IDs copied from `hermes sessions list` work even when the list view truncates them for display
- add SessionDB and CLI regression coverage for prefix-based resolution

## Root cause
`hermes sessions list` prints only the first 20 characters of each session ID, but the session actions were passing the user-provided value straight into exact-match lookups and deletes. A listed ID prefix like `20260315_092437_c9a6` therefore failed to match the real stored ID `20260315_092437_c9a6ff`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_sessions_delete.py`
- `tests/test_hermes_state.py`