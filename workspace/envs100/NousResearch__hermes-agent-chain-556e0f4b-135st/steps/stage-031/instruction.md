**feat(mcp): expose MCP servers as standalone toolsets**

Each configured MCP server now registers as its own toolset in `TOOLSETS` (e.g. `TOOLSETS['github'] = {tools: ['mcp_github_list_files', ...]}`), making raw server names resolvable in `platform_toolsets` overrides.

**Problem:** Gateway sessions using raw toolset names like `['terminal', 'file', 'github']` in `platform_toolsets.telegram` couldn't resolve MCP tools because they were only injected into `hermes-*` umbrella toolsets.

**Solution:** `_sync_mcp_toolsets()` creates a standalone toolset for each MCP server name, plus continues injecting into `hermes-*` sets for the default path. Skips server names that collide with built-in toolsets.

Salvaged from PR #1876 by @kshitijk4poor (MCP toolset feature only — unrelated refactoring dropped).

## Tests
2 new tests (standalone toolset creation + built-in collision guard). All 140 MCP tests pass.