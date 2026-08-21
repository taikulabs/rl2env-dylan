**fix(cli): fall back to main when current branch has no remote counterpart**

## Summary
- salvage the local-only branch update fix from #1044 onto current main
- verify `origin/<current-branch>` exists before counting and pulling updates
- fall back to `origin/main` when the current local branch has no remote counterpart so `hermes update` does not crash
- add regression tests for fallback-to-main, normal remote branch, and already-up-to-date cases

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_cmd_update.py`