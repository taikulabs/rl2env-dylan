**fix(update): drop autostash by stash selector**

## Summary
- resolve the autostash commit hash back to its current stash selector before dropping it
- keep the update successful even if the stash entry can no longer be resolved or dropped
- add regression coverage for selector resolution, successful drop, missing selector, and drop failure

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_autostash.py`