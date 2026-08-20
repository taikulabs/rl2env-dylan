**fix(credential-pool): distinguish OpenRouter upstream 429s from account 429s**

## Summary

An OpenRouter upstream-provider 429 no longer marks `OPENROUTER_API_KEY` exhausted — the key stays usable and the agent falls back to a different model instead.

Root cause: OpenRouter returns 429 in two distinct shapes and the classifier treated them identically, rotating/exhausting the credential on every 429. An *upstream* 429 (DeepSeek/Anthropic/etc. rate-limiting OpenRouter's aggregate traffic) burned the user's healthy key for ~24min, silently disabling context compression, summarization, and vision.

Salvage of #15487 by @znding04 (first-time contributor). The branch was stale and the consumer-side recovery/fallback code had since moved out of `run_agent.py` into `agent/agent_runtime_helpers.py` + `agent/chat_completion_helpers.py` + `agent/conversation_loop.py`; the classifier change applied directly and the consumer edits were reapplied to the relocated code. Authorship preserved.

## Changes

- `agent/error_classifier.py`: new `FailoverReason.upstream_rate_limit`. A 429 with OpenRouter's unambiguous wrapper message `"Provider returned error"` (the same signal the existing `metadata.raw` parser already trusts) classifies as `upstream_rate_limit` with `should_rotate_credential=False`, `should_fallback=True`, and the upstream provider name in `error_context`. Overload disambiguation still runs first.
- `agent/agent_runtime_helpers.py` (`recover_with_credential_pool`): `upstream_rate_limit` short-circuits before any rotation — never marks/exhausts/swaps the credential, defers to the fallback chain.
- `agent/conversation_loop.py`: upstream 429 always falls back to a different model regardless of pool state (the pool can't help when the *upstream* model is throttled), with a distinct "Upstream {provider} rate-limited" status.
- `agent/chat_completion_helpers.py` (`try_activate_fallback`): `upstream_rate_limit` joins the rate_limit/billing cooldown set so leaving-primary cooldown arms correctly.
- `tests/agent/test_error_classifier.py`: 6 new tests (upstream detected, account 429 still rotates, overload precedence, metadata-only shape, empty-context, non-openrouter wrapper not matched).

## Validation

| | Account 429 | Upstream 429 |
|---|---|---|
| Classified reason | `rate_limit` | `upstream_rate_limit` |
| Credential rotated/exhausted | yes ✓ | **no** |
| Recovery | rotate key | fall back to another model |

- `tests/agent/test_error_classifier.py` — 172 pass
- `tests/run_agent/test_provider_fallback.py` + `tests/agent/test_gemini_fast_fallback.py` — 29 pass
- E2E (real `classify_api_error` → real `recover_with_credential_pool`, fake pool): upstream 429 leaves the credential untouched (no rotate, no exhaust, no swap); account 429 still rotates. Exact reported bug closed.

.

## Infographic

![PR #15487 infographic](https://v3b.fal.media/files/b/0aa05c20/OhASiNpkD4WvYnExefWw0_oc31Ciwz.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_error_classifier.py`