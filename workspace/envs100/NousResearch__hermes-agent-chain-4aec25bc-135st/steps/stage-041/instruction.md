**fix(mcp): track exact server provenance to prevent parallel-safe prefix collisions (salvage #27060)**

## Summary
Salvage of #27060 — `is_mcp_tool_parallel_safe()` used prefix matching on tool names (`mcp_{server}_{tool}`), which is ambiguous when server names contain underscores. With parallel-safe server `a` and not-parallel-safe `a_b`, the tool `mcp_a_b_tool` (from server `a_b`) would `startswith("a_")` and be incorrectly flagged parallel-safe — running it concurrently with another tool from `a` could cause real concurrency bugs in MCP servers that haven't opted in.

Fix: track exact `tool_name → server_name` provenance at registration time. `is_mcp_tool_parallel_safe()` becomes a dict lookup.

## Changes
- `tools/mcp_tool.py`:
  - Add `_mcp_tool_server_names: Dict[str, str]` keyed by full prefixed tool name.
  - `_track_mcp_tool_server()` / `_forget_mcp_tool_server()` helpers wired into register and deregister paths (initial registration, `_refresh_tools`, `shutdown`).
  - `is_mcp_tool_parallel_safe()` now reads the dict instead of prefix-matching.
- `tests/tools/test_mcp_tool.py` — new `test_is_mcp_tool_parallel_safe_uses_exact_registered_server` proving the `a` vs `a_b` ambiguity is resolved correctly.
- `tests/run_agent/test_run_agent.py` — existing parallel-batch tests updated to populate the new dict alongside `_parallel_safe_servers`.

## Validation
- `scripts/run_tests.sh tests/tools/test_mcp_tool.py -q` → 195/195 pass.
- `scripts/run_tests.sh tests/run_agent/test_run_agent.py -q -k parallel` → 7/7 pass.

Original PR: #27060 — credit preserved via rebase-merge.