**fix(aux): remove hardcoded Codex fallback model, drop Codex from auto chain**

## Summary

Deletes `_CODEX_AUX_MODEL` and removes `_try_codex` from the auxiliary fallback chain. Codex-OAuth is no longer a second-order fallback that guesses a model ID — if the user's main provider fails, the chain tries OpenRouter / Nous / custom / api-key and stops, instead of rolling through a hardcoded Codex model that OpenAI silently rotates out of its ChatGPT-account allow-list.

. Supersedes #17544 (which reset the stale-constant clock rather than removing it).

## Why not the one-line constant bump

That constant has already drifted twice in 6 weeks:

| Date | Value | Status |
|---|---|---|
| pre-Mar 2026 | `gpt-5.3-codex` | rejected by ChatGPT-account Codex |
| 735a6e76 (Mar 2026) | `gpt-5.2-codex` | worked briefly |
| #17533 (Apr 29 2026) | `gpt-5.2-codex` | rejected; only gpt-5.x model that's rejected per @pokibao's test matrix |
| #17544 proposal | `gpt-5.4` | works today, will drift again |

ChatGPT-account Codex allow-list is undocumented and OpenAI publishes no changelog. Any pinned default rots — the question is just "how soon."

## Changes

| File | Change |
|---|---|
| `agent/auxiliary_client.py` | Delete `_CODEX_AUX_MODEL`; rename `_try_codex` -> `_build_codex_client(model)` requiring explicit model; drop Codex from `_get_provider_chain` (5 rungs -> 4); drop Codex from `provider=custom` fallback ladder; route `_resolve_strict_vision_backend("openai-codex")` through `resolve_provider_client` so caller's model is honored; update module docstring |
| `tests/agent/test_auxiliary_client.py` | Update chain-length test (4 entries, asserts Codex is NOT in chain); replace `test_skips_to_codex_when_or_and_nous_fail` with `test_codex_not_in_fallback_chain`; update `_try_codex` -> `_build_codex_client` tests; refresh test model strings gpt-5.2-codex -> gpt-5.4 |
| `tests/agent/test_codex_cloudflare_headers.py` | `_try_codex` -> `_build_codex_client("gpt-5.4")`; raw_codex test now passes explicit `model=` |
| `tests/run_agent/test_provider_parity.py` | `test_codex_fallback_last_resort` -> `test_codex_not_in_auto_fallback` (inverted assertion — verifies (None, None) is returned) |

## Behavior

| User setup | Before | After |
|---|---|---|
| main=openai-codex, any model | Uses user's configured model via Step 1 | Unchanged |
| main=openrouter, has codex auth, OR has payment error | Fallback chain hits Codex, tries `gpt-5.2-codex`, fails with "not supported" | Fallback chain stops at api-key; 60s pause with cleaner logs |
| `auxiliary.<task>.provider: openai-codex` with `model` set | Works (user specifies model) | Unchanged |
| `auxiliary.<task>.provider: openai-codex` with NO model | Silently uses `gpt-5.2-codex` | Warns "pass model explicitly" and returns None |

## Validation

```
tests/agent/                                 2220 passed
tests/run_agent/test_provider_parity.py       113 passed
tests/run_agent/test_provider_fallback.py       9 passed
tests/run_agent/test_compressor_fallback_update.py   passed
E2E: removed symbols gone                    PASS
E2E: chain is 4 rungs, no openai-codex       PASS
E2E: payment fallback returns (None, None)   PASS
E2E: Step 1 Codex-main user path unaffected  PASS (gpt-5.4, gpt-5.5 both honored)
E2E: explicit model=None warns, returns None PASS
```

Credit: @pokibao for the test matrix + root-cause analysis, @afurm for the constant-bump proposal that surfaced this as worth a proper fix.