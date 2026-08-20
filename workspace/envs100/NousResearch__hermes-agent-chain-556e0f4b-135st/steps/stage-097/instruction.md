**fix(auth): preserve 'custom' provider instead of silently remapping to 'openrouter'**

## Summary

. `resolve_provider('custom')` was silently returning `'openrouter'`, causing users who set `provider: custom` in config.yaml to unknowingly route through OpenRouter instead of their local/custom endpoint.

This is Phase 1 of the `/model` command overhaul plan.

## What changed

- **`hermes_cli/auth.py`**: Split the `{"openrouter", "custom"}` set check into two separate conditionals so `'custom'` returns `'custom'` as-is
- **`hermes_cli/runtime_provider.py`**: 
  - `_resolve_named_custom_runtime()` now returns `provider='custom'` instead of `'openrouter'`
  - `_resolve_openrouter_runtime()` returns `provider='custom'` when that was explicitly requested
  - Adds `'no-key-required'` placeholder API key for local servers that don't need authentication (OpenAI SDK requires non-empty string)
- **Tests**: Updated 1 existing test + added 5 new tests covering the fix

## Why this is safe

All OpenRouter-specific logic in `run_agent.py` checks by URL (`"openrouter" in base_url`), not by provider name. Custom endpoints hitting non-OpenRouter URLs won't match any OpenRouter-specific behavior.

## Salvaged from

. Four external PRs attempted this fix (#2564, #2571, #2633, #2725) — all submitted the same auth.py change but none added the runtime_provider.py fixes or the no-key-required fallback for local servers. Credit to @davidmacmillan for the original report, @aifunmobi for the root cause analysis, and @teyrebaz33, @dusterbloom, @amethystani for their fix attempts.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_runtime_provider_resolution.py`