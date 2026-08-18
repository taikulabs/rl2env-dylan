**fix: retry 3 times with nudge when model returns truly empty response**

## Summary

Fills the last gap in the empty-response recovery chain. When a model returns **no content, no structured reasoning, and no tool calls** (common with open models via OpenRouter/Ollama), the agent now nudges the model up to 3 times before falling through to `(empty)`.

### Problem

Open models sometimes return completely blank responses — no content field, no reasoning, no tool calls. PR #5278 removed the old retry cascade (correctly, for reasoning-only responses), and PR #5931 added thinking prefill continuation for structured reasoning. But neither covers the case where the model produces **absolutely nothing**. Users on Discord/Telegram see `(empty)` as a visible message.

### Recovery chain (complete)

| Step | Condition | Action |
|------|-----------|--------|
| 1 | Prior tool turn had content | Use `_last_content_with_tools` fallback |
| 2 | Structured reasoning, no text | Thinking prefill continuation |
| 3 | **Truly empty (no content, no reasoning)** | **Nudge retry up to 3 times (NEW)** |
| 4 | All recovery exhausted | `(empty)` terminal |

### What changed

**run_agent.py**: Between the thinking prefill path and the `(empty)` terminal, added a nudge retry loop. Each retry:
- Appends the empty assistant message (maintains role alternation)
- Appends a system nudge: `[System: Your last response was empty. Please provide a response to the user.]`
- Continues the agent loop

Gated on `_truly_empty` (content is None or whitespace-only) AND `not _has_structured` (no API reasoning fields). Inline `<think>` blocks are excluded — the model chose to reason, it just produced no visible text.

**tests/run_agent/test_run_agent.py**:
- Updated `test_truly_empty_response` → expects 4 API calls (1 original + 3 retries)
- Added `test_truly_empty_response_succeeds_on_nudge` — model produces content after 1 nudge

### Test results
```
6 passed (empty_response + truly_empty + reasoning_only tests)
674 passed total in run_agent suite (7 pre-existing failures in test_agent_loop_tool_calling unrelated)
```