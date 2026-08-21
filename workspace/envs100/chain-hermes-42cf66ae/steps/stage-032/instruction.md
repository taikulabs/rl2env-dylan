**feat(gateway): salvage reasoning hot reload from #938**

## Summary
- 
- reload `agent.reasoning_effort` from config before each gateway/background `AIAgent(...)` construction so the next turn picks up config changes
- add `/reasoning` entry exposure for Telegram and Discord while keeping the richer current-main `/reasoning` command behavior intact
- add regression coverage for config-first reasoning resolution, stale env fallback behavior, and `/reasoning` state refresh

Original contributor work salvaged from #938 by @PeterFile.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_reasoning_command.py`