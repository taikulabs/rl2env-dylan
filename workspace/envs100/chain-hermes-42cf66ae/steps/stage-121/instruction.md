**feat: auto-detect provider when switching models via /model**

## Summary

Fixes the confusing /model experience where typing `/model deepseek-chat` while on a different provider would silently keep the wrong provider, causing API errors.

Salvages the concept from PR #1177 by @virtaava, with credential awareness and OpenRouter slug mapping added.

### What changed

**Auto-detection in /model** (cli.py + gateway/run.py):
- When no explicit `provider:model` syntax is given, `detect_provider_for_model()` finds the right provider
- Priority: direct provider with creds → OpenRouter slug match → direct provider without creds
- Bare model names get remapped to proper OpenRouter slugs (`gpt-5.4` → `openai/gpt-5.4`)

**DeepSeek as first-class provider** (auth.py + config.py + models.py):
- Registered in `PROVIDER_REGISTRY` as an API-key provider
- `DEEPSEEK_API_KEY` env var, base URL `https://api.deepseek.com/v1`
- Static catalog: `deepseek-chat`, `deepseek-reasoner`
- Works through the existing generic API-key credential resolution path — no changes to runtime_provider.py needed

**New functions in models.py:**
- `detect_provider_for_model(model, current_provider)` → `(provider, model)` or `None`
- `_find_openrouter_slug(bare_name)` → full OpenRouter model ID

### Examples
```
# Before: silently stays on openai-codex, API error
/model deepseek-chat

# After: auto-switches to deepseek provider (if DEEPSEEK_API_KEY set)
# or remaps to deepseek/deepseek-chat on OpenRouter
/model deepseek-chat

# Bare names get proper slugs
/model gpt-5.4        → openai/gpt-5.4
/model claude-opus-4.6 → anthropic/claude-opus-4.6

# Explicit syntax still works as before
/model anthropic:claude-opus-4-6
```

### Tests
- 11 new tests for `detect_provider_for_model` and `_find_openrouter_slug`
- Updated existing tests for new behavior
- Full suite: 4548 passed, 0 regressions

 (concept salvaged with improvements)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_models.py`
- `tests/test_cli_model_command.py`
- `tests/tools/test_local_env_blocklist.py`