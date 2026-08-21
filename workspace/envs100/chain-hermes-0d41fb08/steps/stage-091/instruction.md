**fix: MiniMax/Alibaba incorrectly detected as OAuth Claude, causing mcp_ tool prefix**

## Summary

MiniMax and Alibaba users on Anthropic-compatible endpoints were getting all tools prefixed with `mcp_` (e.g. `mcp_terminal`, `mcp_web_search`) and system prompts injected with Claude Code identity. Reported by stefan171.

## Root Cause

`_is_oauth_token()` used a broad catch-all: anything NOT starting with `sk-ant-api` was treated as an OAuth token. MiniMax/Alibaba API keys don't start with `sk-ant-api`, so they falsely triggered the OAuth/Claude Code path:
- All tool names prefixed with `mcp_`
- `You are Claude Code` injected into system prompt
- `Hermes Agent` replaced with `Claude Code` throughout

## Fix

Changed `_is_oauth_token()` from a broad exclusion ("not an API key → must be OAuth") to positive identification of actual Anthropic OAuth token formats:
- `sk-ant-*` (but not `sk-ant-api-*`) → setup tokens, managed keys
- `eyJ*` → JWTs from Anthropic OAuth flow
- Everything else → `False`

One function, one fix. No endpoint/provider checks needed — the token format itself is the signal.

## Changes
- `agent/anthropic_adapter.py` — rewrote `_is_oauth_token()` with positive matching
- `tests/agent/test_anthropic_adapter.py` — updated managed key test (format without Anthropic prefix correctly returns False; managed keys enter via diagnostics-only path, not normal token resolution)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_anthropic_adapter.py`