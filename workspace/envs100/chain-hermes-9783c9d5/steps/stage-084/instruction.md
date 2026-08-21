**feat(providers): add ordered fallback provider chain (salvage #1761)**

## Summary

Salvage of #1761 by @uzaylisak. Extends the single `fallback_model` mechanism into an ordered provider chain. When the primary model fails (rate limit, 4xx, connection error), Hermes tries each fallback in sequence until one succeeds.

.

## Config

```yaml
# New list format — tried in order
fallback_providers:
  - provider: openrouter
    model: anthropic/claude-sonnet-4
  - provider: openai
    model: gpt-4o
  - provider: zai
    model: glm-4.7
```

Legacy single-dict `fallback_model` format still works unchanged.

## Key fix vs original PR

The original PR modified `_try_activate_fallback()` to use a chain index but did NOT update the call sites. Several call sites guarded with `not self._fallback_activated`, which prevented the chain from ever advancing past provider #1. This salvage replaces those guards with `self._fallback_index < len(self._fallback_chain)` so the chain actually works.

Additionally, when a provider in the chain fails to resolve (unconfigured, auth error, etc.), the chain now skips to the next entry instead of stopping.

## Changes

| File | Change |
|------|--------|
| `run_agent.py` | `_fallback_chain` + `_fallback_index` replaces one-shot `_fallback_model`; call sites updated |
| `cli.py` | Reads `fallback_providers` with legacy `fallback_model` compat |
| `gateway/run.py` | Same |
| `hermes_cli/config.py` | `fallback_providers: []` in DEFAULT_CONFIG |
| `tests/test_provider_fallback.py` | 12 new tests for chain init, advancement, skip behavior |
| `tests/test_run_agent.py` | 5 existing test fixtures updated for new attributes |
| `tests/test_compressor_fallback_update.py` | 1 fixture updated |

## Live test results

Tested with real OpenRouter API — primary model 404s, chain advances through fallbacks:

```
Primary: openai/fake-model-1 → 400 "not a valid model ID"
  ⚠️ Non-retryable error (HTTP 400) — trying fallback...
  🔄 switching to: openai/fake-model-2 (openrouter)
Fallback #1: openai/fake-model-2 → 400 "not a valid model ID"
  ⚠️ Non-retryable error (HTTP 400) — trying fallback...
  🔄 switching to: anthropic/claude-sonnet-4 (openrouter)
Fallback #2: anthropic/claude-sonnet-4 → ✓ "chain works"
```

## Test results

6806 passed, 9 pre-existing failures, 0 regressions.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_compressor_fallback_update.py`
- `tests/test_provider_fallback.py`
- `tests/test_run_agent.py`