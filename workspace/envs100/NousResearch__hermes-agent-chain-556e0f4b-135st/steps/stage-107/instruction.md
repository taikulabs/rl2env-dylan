**fix: GLM reasoning-only and max-length handling**

## Summary

Salvage of PR #2993 by @kshitijk4poor.

Three improvements for GLM/Z.AI and models that embed reasoning inline:

1. **Overflow detection** — adds `'prompt exceeds max length'` to context overflow strings so Hermes compresses and retries instead of erroring out on GLM 400s.

2. **Inline reasoning extraction** — extends `_extract_reasoning()` to pull reasoning from inline content blocks when no structured API reasoning fields are present (fallback only).

3. **Reasoning-only response salvage** — the existing retry-and-salvage code (line ~7033) now actually fires for models that embed reasoning inline, since `_extract_reasoning()` can find it.

## Bug fix on top of original PR

Added `if not reasoning_parts:` guard so inline extraction only runs as a fallback when no structured API reasoning exists. Without this, `test_structured_reasoning_takes_priority` failed — structured reasoning got concatenated with inline blocks.

## Live test results

Tested against all available providers:
- OpenRouter (claude-sonnet-4, gpt-4.1, deepseek-r1, deepseek-v3, qwen3-235b) — all PASS
- Anthropic direct (claude-sonnet-4, with and without tools) — all PASS
- Qwen3 naturally triggered the reasoning salvage path — confirmed working

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_run_agent.py`