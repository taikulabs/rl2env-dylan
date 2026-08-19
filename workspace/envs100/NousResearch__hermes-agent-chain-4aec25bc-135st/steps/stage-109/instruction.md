**feat(kanban): add optional board parameter to all MCP tools**

Salvages #27598 by @nnnet.

Adds optional `board` parameter to all 9 `kanban_*` MCP tools via shared `_connect` helper. Backwards compatible — omitting `board` keeps current pinned-board behavior. Useful for orchestrator profiles that route across multiple boards.

Two-file scope: `tools/kanban_tools.py` + tests.

Original branch had small conflicts where main had added unrelated fields (`artifacts` schema property, worker-session metadata stamping) to the same dicts the PR touched; resolved by keeping both. Authorship preserved via rebase merge.

## Validation
- 14 board-related tool tests pass.