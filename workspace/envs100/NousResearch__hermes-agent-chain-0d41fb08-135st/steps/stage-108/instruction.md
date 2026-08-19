**feat: warn at session start when compression model context is too small**

## Summary

Adds a session-start check that detects when the auxiliary compression model's context window is smaller than the main model's compression threshold. When this is the case, context compression will not be possible because the content to summarize will exceed the auxiliary model's capacity.

## What changed

**`run_agent.py`:**
- New method `_check_compression_model_feasibility()` on `AIAgent`
- Called during `__init__` right after the compressor is initialized
- Resolves the auxiliary compression model via the same resolution chain as `call_llm(task='compression')` — respects `auxiliary.compression.model`, `compression.summary_model`, env overrides, and the auto-detection chain
- Compares the auxiliary model's context length against `threshold_tokens` (= `main_context * threshold_percent`)
- Emits warning via `_emit_status()` — covers **all platforms**: CLI (`_vprint(force=True)`), and every gateway platform (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Home Assistant, DingTalk, etc.) through `status_callback('lifecycle', ...)`
- Also logs via `logger.warning()` to agent.log
- Warns when no auxiliary LLM provider is configured at all
- Entire check is wrapped in try/except — never blocks startup

**`tests/run_agent/test_compression_feasibility.py`:** 8 tests covering:
- Warning fires when aux context < threshold
- No warning when aux context >= threshold
- No provider configured → different warning
- Compression disabled → check skipped
- Exception safety (never crashes)
- Gateway status_callback receives the warning
- Exact boundary (equal = no warning)
- One below boundary → warning fires

## Example output

When a user has a 200K main model (threshold at 100K) but their auxiliary compression model only has 32K context:
```
📊 Context limit: 200,000 tokens (compress at 50% = 100,000)
⚠ Compression model (google/gemini-3-flash-preview) context is 32,768 tokens,
but the main model's compression threshold is 100,000 tokens. Context compression
will not be possible — the content to summarise will exceed the auxiliary model's
context window. Consider configuring a larger model via auxiliary.compression.model
in config.yaml.
```