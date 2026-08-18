**fix(tools,cli): normalise MCP schemas + expand session list columns**

## Summary

Two salvaged bug fixes on current main.

### 1. Normalise MCP object schemas without properties (PR #2095 by @sammcf)

Normalises MCP tool input schemas that declare `{"type": "object"}` without a `properties` field before forwarding them to the LLM tool-calling API. Fixes a `400 Bad Request` from OpenAI when an MCP server exposes a bare object schema (e.g. Crawl4AI's `ask` tool).

- Added `_normalize_mcp_input_schema()` in `tools/mcp_tool.py`
- Applied to both MCP tool discovery and the sampling callback
- Regression tests for both code paths

Cherry-picked from #2095 with authorship preserved.

### 2. Expand session list columns for full ID visibility (PR #2085 by @Nebula037, )

`hermes sessions list` was truncating session IDs to 20 chars (`[:20]`), cutting off the last 2-4 characters. This made it impossible to copy the correct ID for `--resume`.

- Removed `[:20]` truncation — full IDs now shown
- Widened title column from 20→30 chars
- Adjusted header/separator widths

Based on #2085 with a correction: the original PR accidentally replaced the no-titles layout (`Preview/Src` header) with a duplicate of the has-titles layout (`Title/Preview` header), misaligning columns when sessions have no titles.