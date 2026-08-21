**fix(tui): respect max turns config**

## Summary
-  by rebuilding the contributor fix on current `main` instead of carrying the stale conflicted branch forward
- reads `agent.max_turns` consistently for TUI session agents, background agents, and `config.show`
- keeps legacy root `max_turns` as a fallback before using the existing defaults
- includes the original author as coauthor and adds regression coverage for `agent: null`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_tui_gateway_server.py`