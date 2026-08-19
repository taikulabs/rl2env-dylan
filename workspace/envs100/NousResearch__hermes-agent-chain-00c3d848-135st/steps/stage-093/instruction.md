**fix(compression): retry summary on main model for unknown errors before giving up**

## Summary

Compression now retries on the main model for any summary failure where the summary model differs from main — not just the `_is_model_not_found` fast-path. Losing N turns of context is almost always worse than one extra summary attempt.

## Why

`_generate_summary` already falls back to the main model when the summary LLM call returns an error that matches `_is_model_not_found` (404/503, `model_not_found`, `does not exist`, `no available channel`). Other misconfig errors — 400s from aggregators, provider-specific "no route" strings, opaque provider rejections — fall straight through to the transient-cooldown branch, which drops the turns and inserts a static placeholder.

Motivation: @0xViviennn spent 2+ hours debugging silent context loss caused by a misconfigured `auxiliary.compression.model`. PR #16771 made the failure visible via a gateway warning. This PR makes the common misconfigurations self-heal instead.

## Changes

`agent/context_compressor.py` — after the existing `_is_model_not_found` retry, add a second best-effort retry-on-main for any other exception when `summary_model != model`. Guarded by `_summary_model_fallen_back` (same flag as the existing path) so there's at most one retry per compressor instance.

## Validation

| | Before | After |
|---|---|---|
| 404 → retry on main | ✓ | ✓ |
| 400 / unknown error → retry on main | ✗ (drops turns, placeholder) | ✓ |
| `summary_model == main_model` | no retry | no retry (same — no loop) |
| Retry itself fails | drops turns after 1 call | drops turns after 2 calls, flag set |

```
scripts/run_tests.sh tests/agent/test_context_compressor.py tests/gateway/test_session_hygiene.py tests/gateway/test_compress_command.py
85 passed in 1.79s
```

4 new tests in `TestSummaryFallbackToMainModel` cover both retry paths, the same-model no-op, and the double-failure bound.

.