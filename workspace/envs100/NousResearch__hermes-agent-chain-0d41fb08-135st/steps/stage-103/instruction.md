**fix(qwen): correct context lengths for qwen3-coder models and send max_tokens to portal**

## Summary

Salvage of PR #7285 by @kshitijk4poor onto current main.

Two bugs affecting Qwen OAuth/Portal users:

**1. Wrong context window** — `qwen3-coder-plus` showed 128K instead of 1M. The generic `"qwen": 131072` catch-all in `DEFAULT_CONTEXT_LENGTHS` matched all Qwen models.

Fix: Added specific entries before the catch-all:
- `qwen3-coder-plus`: 1,000,000 (1M) — **corrected from PR's 1,048,576** per official Alibaba Cloud docs and OpenRouter listing
- `qwen3-coder`: 262,144 (256K)

**2. Random stopping** — `max_tokens` was explicitly suppressed for Qwen Portal, so the server applied its own low default. Reasoning models exhaust that budget on thinking tokens and return `finish_reason="stop"` with truncated output.

Fix: Honor explicit `max_tokens` when set. When `max_tokens` is None, send 65,536 (documented max output for qwen3-coder models). Mirrors the existing OpenRouter+Claude pattern.

## Changes
- `agent/model_metadata.py` — 2 new context length entries
- `run_agent.py` — Remove Qwen Portal max_tokens suppression, add default
- `tests/agent/test_model_metadata.py` — 3 new context length tests
- `tests/run_agent/test_run_agent.py` — Updated + new max_tokens tests

## Tests
- 80 model_metadata tests passing
- 16 BuildApiKwargs tests passing