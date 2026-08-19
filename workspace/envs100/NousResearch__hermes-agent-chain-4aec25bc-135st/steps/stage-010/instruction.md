**feat(mcp): supports_parallel_tool_calls for MCP servers (salvage of #9944)**

## Summary
Salvage of #9944 — MCP servers can opt-in to parallel tool execution by setting `supports_parallel_tool_calls: true` in their config. Tools from opted-in servers can run concurrently within a single tool-call batch, matching the behavior already available for read-only built-ins like `web_search` and `read_file`.

Port from openai/.

## Why salvage
Original PR is 4,266 commits stale. Cherry-picking onto current main hit one conflict in `tools/mcp_tool.py` (circuit breaker module-level state block was added on main between the PR's branch point and today) — resolved by keeping main's block and appending the PR's `_parallel_safe_servers` set. Also fixed two tests that mocked `_sync_mcp_toolsets`, a helper that no longer exists on main.

## Changes
- `tools/mcp_tool.py`: `_parallel_safe_servers` module-level set, populated during `register_mcp_servers()` (idempotent, handles toggling). New public `is_mcp_tool_parallel_safe(tool_name)` walks registered prefixes (server names can contain underscores after sanitization).
- `run_agent.py`: lazy-import wrapper `_is_mcp_tool_parallel_safe()`. `_should_parallelize_tool_batch()` now consults it for MCP tools that aren't in the static `_PARALLEL_SAFE_TOOLS` set.
- 11 new tests covering server tracking, toggle behavior, prefix lookup, integration with `_should_parallelize_tool_batch`.
- Docs: `mcp.md` + `mcp-config-reference.md` updated.

## Validation
| | Result |
|---|---|
| `tests/tools/test_mcp_tool.py` | 193/193 |
| `tests/run_agent/test_run_agent.py` + parallel MCP tests | 336/336 |
| E2E (manual): opted-in detection, non-opted, non-MCP, edge cases, run_agent lazy import | All OK |

## Architectural note
Codex implements this through `ToolRouter` at the Rust crate level. We use a module-level set populated during server registration and queried via `is_mcp_tool_parallel_safe(tool_name)`, which handles underscores-in-server-names by checking all registered parallel-safe prefixes. Same external behavior, different glue.

## Credit
@teknium1's original scout work in #9944. This PR salvages it onto current main.