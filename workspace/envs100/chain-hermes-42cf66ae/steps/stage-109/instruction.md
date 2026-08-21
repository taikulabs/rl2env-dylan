**fix: reduce file tool log noise**

## Summary
- stop checkpoint_manager from logging `git diff --cached --quiet` exit code 1 as an error during normal successful checkpoints
- downgrade expected write denials (`PermissionError`, `EACCES`, `EPERM`, `EROFS`) out of `ERROR` logging in `write_file_tool`
- add regression tests covering both behaviors

## Why
These conditions were making the CLI error log look much noisier than the real runtime health:
- `git diff --cached --quiet` returns `1` when staged changes exist, which is expected during a successful checkpoint
- expected write denials like read-only filesystem were being logged as `ERROR` even when the tool was correctly returning a user-facing error JSON

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_checkpoint_manager.py`
- `tests/tools/test_file_tools.py`