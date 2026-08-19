**fix: add vLLM/local server error patterns + MCP initial connection retry**

## Summary

Two improvements ported from analysis of [Kilo-Org/kilocode](https://github.com/Kilo-Org/kilocode) merged PRs (weekly scout, week of 2026-04-06):

### 1. vLLM / Local Server Context Overflow Error Patterns

**Problem:** Local inference servers (vLLM, Ollama, llama.cpp) return context overflow errors in formats that our error classifier doesn't recognize. For example:
- vLLM: `"The engine prompt length 1327246 exceeds the max_model_len 131072"`
- Ollama: `"context length exceeded"`
- llama.cpp: `"slot context: 4096 tokens, prompt 8192 tokens"`

Without matching these patterns, context overflow errors are misclassified as generic format errors, causing the agent to retry instead of triggering context compression.

**Fix:** Added 7 new patterns to `_CONTEXT_OVERFLOW_PATTERNS` in `error_classifier.py` covering vLLM (`max_model_len`, `prompt length`, `input is too long`), Ollama (`context length exceeded`), and llama.cpp/llama-server (`slot context`, `n_ctx_slot`).

**Source:** Inspired by Kilo Code's vLLM context overflow detection improvement (OpenCode v1.3.0, upstream #17763).

### 2. MCP Initial Connection Retry with Backoff

**Problem:** When an MCP server's first connection attempt fails (e.g., transient DNS failure at agent startup), the server is permanently marked as failed — no retry. This is inconsistent with post-connect reconnection, which retries up to 5 times with exponential backoff. A brief DNS blip during agent startup permanently disables any MCP server.

**Fix:** Initial connection now retries up to 3 times (`_MAX_INITIAL_CONNECT_RETRIES`) with exponential backoff before giving up. Shutdown is respected during backoff sleep. This matches the resilience of the existing post-connect reconnection path.

**Source:** Inspired by Kilo Code's MCP server resilience fixes (OpenCode v1.3.3, upstream #19042 — "Fix MCP servers disappearing after transient errors").

## Changes

| File | Change |
|------|--------|
| `agent/error_classifier.py` | +12 lines: 7 new context overflow patterns for local servers |
| `tools/mcp_tool.py` | +29 lines: initial connection retry loop with backoff |
| `tests/agent/test_error_classifier.py` | +42 lines: 6 new tests for vLLM/Ollama/llama.cpp errors |
| `tests/tools/test_mcp_stability.py` | +110 lines: 4 new tests for initial connection retry |
| `tests/tools/test_mcp_tool.py` | Updated existing test to expect retry behavior |

## Test Results

All 276 affected tests pass:
- `tests/agent/test_error_classifier.py`: 97 passed
- `tests/tools/test_mcp_stability.py`: 16 passed
- `tests/tools/test_mcp_tool.py`: 163 passed