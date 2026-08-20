**fix: clearer terminal backend requirement errors**

## Summary
- salvage PR #979 onto current main without regressing newer terminal backend checks
- log actionable errors for unknown TERMINAL_ENV values, missing SSH host/user, and missing Modal credentials/config
- add deterministic regression tests for the new preflight logging paths

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_terminal_requirements.py`