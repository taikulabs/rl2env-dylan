**fix(kimi): force fixed temperature on kimi-k2.* models (k2.5, thinking, turbo)**

## Summary

Hermes already has a fixed-temperature override path for Moonshot's coding endpoint (added in #11834 / #11933), but the dictionary key is the **provider** string `kimi-for-coding`, while the lookup is against the **model** name (e.g. `kimi-k2.5`, `kimi-k2-turbo-preview`, `kimi-k2-thinking`). So the override never fires for real model IDs and users hit:

```
BadRequestError [HTTP 400]
Model: kimi-k2.5
Endpoint: https://api.kimi.com/coding/v1
Error: HTTP 400: invalid temperature: only 0.6 is allowed for this model
```

This PR expands `_fixed_temperature_for_model()` to actually match the kimi-k2 model family, consistent with Moonshot's documented requirements:

- `kimi-k2-thinking` / `kimi-k2-thinking-turbo` → **1.0** (thinking mode)
- all other `kimi-k2.*` (k2.5, k2-turbo-preview, k2-0905-preview, …) → **0.6** (non-thinking / instant mode)

It also tolerates an optional vendor prefix (e.g. `moonshotai/kimi-k2.5`) so aggregator routings are covered.

All three existing call sites (`_build_call_kwargs`, main chat loop, and `flush_memories` paths in `run_agent.py`) already delegate to `_fixed_temperature_for_model`, so no other files need to change — they just start seeing the right value.

### Why this over "omit temperature" (cf. #12132)

Moonshot explicitly documents that these models require those specific temperatures — 1.0 is needed for thinking-mode quality, and 0.6 is the instant-mode lock. Omitting the parameter leans on provider defaults, which may differ across aggregators (Fireworks' kimi_k2.5 also enforces 1.0 for thinking mode, per anomalyco/). Setting the correct value is explicit and portable.

## Changes

- `agent/auxiliary_client.py` — `_fixed_temperature_for_model()` now prefix-matches `kimi-k2*` (with optional `vendor/` prefix) and routes thinking vs non-thinking.
- `tests/agent/test_auxiliary_client.py` — Added a parametrized test covering k2.5, k2-turbo-preview, k2-0905-preview, k2-thinking, k2-thinking-turbo, and the `moonshotai/` prefix form. Fixed the previously mis-named `test_non_kimi_model_still_preserves_temperature` (which used `kimi-k2.5` as the "non-kimi" model) to use a truly non-kimi model.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_auxiliary_client.py`