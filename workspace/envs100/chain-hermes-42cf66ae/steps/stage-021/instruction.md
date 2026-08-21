**fix: keep Honcho recall out of the cached system prefix**

## Summary
- keep later-turn Honcho recall out of the system prompt so the stable cache prefix does not churn
- attach later-turn Honcho recall to the current-turn user message at API-call time only
- add regression tests for the helper and continuing-session behavior

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_run_agent.py`