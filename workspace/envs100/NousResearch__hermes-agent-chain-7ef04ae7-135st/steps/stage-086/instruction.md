**fix(aux): preserve provider identity for resolved endpoints**

## Summary
MoA reference slots and auxiliary tasks keep their first-class provider identity when runtime resolution hands back both a provider and a concrete `base_url`, instead of being flattened to `custom`.

Root cause: `_resolve_task_provider_model()` forced `provider="custom"` whenever any `base_url` was present. Correct for bare/custom endpoints, but wrong for provider-backed routes (anthropic, qwen-oauth, minimax-oauth, openai-codex, xai-oauth, nous, copilot) whose provider branch adds OAuth refresh, transport, and request-shaping. A MoA Codex reference therefore hit `chatgpt.com/backend-api/codex` as a plain custom endpoint — no Cloudflare headers — got HTML back, and surfaced as a spurious "rate-limited" on the first turn (the support thread that prompted this).

## Changes
- `agent/auxiliary_client.py`: add `_preserve_provider_with_base_url()`; first-class providers paired with a resolved `base_url` keep their identity. Bare `base_url`, `custom`/`custom:*`, `auto`, unknown providers, and the direct `openai` alias still route through `custom`. Primary check is the provider catalog (`get_provider`), with a static high-risk allow-list as the import-safe fallback.
- `tests/agent/test_auxiliary_client.py`: `TestResolveTaskProviderModel` — identity preserved for first-class providers, custom routing for bare/custom/unknown and the openai alias.
- `tests/run_agent/test_moa_loop_mode.py`: provider-backed slot survives `_slot_runtime()` + aux resolution (`api_mode` is handled separately by `call_llm`, so it's not passed to the resolver).

## Validation
| | Before | After |
|---|---|---|
| `openai-codex` ref slot (with base_url) | `custom` → Cloudflare HTML → false 429 | `openai-codex` → correct transport |
| `anthropic`/`qwen-oauth`/`minimax-oauth` ref | flattened to `custom` | identity preserved |
| bare base_url / `openai` alias | `custom` | `custom` (unchanged) |

`scripts/run_tests.sh tests/agent/test_auxiliary_client.py tests/run_agent/test_moa_loop_mode.py` → 278 passed, 0 failed. E2E resolution chain verified with real imports.

Salvaged from #54425 by @helix4u onto current `main` (the original branch was 332 commits stale and its diff reverted unrelated recent fixes). His authorship is preserved on the commit; the resolver logic and tests are his, reconciled with main's current `api_mode` propagation contract.

## Infographic

![provider-identity-preserved](https://v3b.fal.media/files/b/0aa05cdc/u7U9Jon8aWeDhyUAQ-j1C_usONQrHY.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_auxiliary_client.py`
- `tests/run_agent/test_moa_loop_mode.py`