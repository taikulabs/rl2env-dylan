**fix: align MiniMax provider with official API docs**

## Summary

Salvage of PR #7096 by @kshitijk4poor. Cherry-picked onto current main with contributor authorship preserved.

Aligns MiniMax provider with official API documentation ([source](https://platform.minimax.io/docs/api-reference/text-anthropic-api)). Fixes 6 bugs:

1. **Transport mismatch** — `providers.py` had `openai_chat` for minimax, should be `anthropic_messages`
2. **Credential leak in `switch_model()`** — fell back to `resolve_anthropic_token()` for all `anthropic_messages` providers, sending Anthropic creds to MiniMax
3. **Prompt caching sent to MiniMax** — `is_native_anthropic` was set from `api_mode` alone, now requires `provider == "anthropic"`
4. **Dot-to-hyphen corruption** — `MiniMax-M2.7` → `MiniMax-M2-7` (model-not-found). Added minimax to preserve-dots set
5. **Trajectory compressor 404** — raw `/anthropic` URL → OpenAI SDK appended `/chat/completions` (404). Now uses `_to_openai_base_url()`
6. **Doctor health check** — MiniMax entries had `None` URL. Now uses `/v1/models`

Also corrects:
- Context window: 204,800 (was 1M/1.048M)
- Model catalog: M2.7/M2.5/M2.1/M2 only (M1 not on /anthropic endpoint)
- Thinking: fully supported in manual mode (was blocked)
- Max output: 131,072 tokens

## Salvage notes

- Dropped `test_setup_model_selection.py` change (file was deleted from main in dead code cleanup)
- 39 tests added/updated across 9 test classes
- 2562 passed, 6 pre-existing flaky failures (pass in isolation)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_minimax_provider.py`