**fix(auxiliary): propagate explicit_api_key to _try_openrouter (salvage #18341)**

`resolve_provider_client()` receives `explicit_api_key` from the credential pool and correctly forwards it to every provider — except OpenRouter, where it called `_try_openrouter()` with no arguments, silently dropping the key. Auxiliary tasks falling back to OpenRouter with a pool-sourced runtime key then auth-failed because the key never reached the client constructor.

## What changed
- `agent/auxiliary_client.py`: add `explicit_api_key: str = None` to `_try_openrouter()`, prefer it over pool-runtime-key and over the `OPENROUTER_API_KEY` env var at both branches. `resolve_provider_client()` passes it through.
- `tests/agent/test_auxiliary_client.py`: 2 regression tests — explicit key wins over env fallback; env fallback still works when no explicit key.

## Why not #18618
@liuhao1024 opened a follow-up that added an early-return branch short-circuiting the whole `_try_openrouter()` flow when `explicit_api_key` is set. That's more code than needed and bypasses the pool-entry base_url resolution. #18341's approach — threading the override through the existing pool-first, env-fallback flow as `explicit_api_key or ...` — is the cleaner implementation and already has test coverage. Closing #18618 in favour of this.

## Validation
- `scripts/run_tests.sh tests/agent/test_auxiliary_client.py` → 117 passed (115 existing + 2 new).
- E2E with mocked `OpenAI` constructor —
  1. explicit key only → client built with explicit key.
  2. env var only → client built with env key.
  3. Both set → explicit wins.

.