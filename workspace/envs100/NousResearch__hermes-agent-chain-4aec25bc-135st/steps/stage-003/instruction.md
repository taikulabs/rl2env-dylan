**fix(auxiliary): resolve xAI OAuth compression from pool**

Salvage of #26678 by @helix4u onto current main.

## Summary
Fixes xAI Grok OAuth auxiliary tasks (compression, vision, etc.) when the user's xAI OAuth credential only lives in the credential pool, not the singleton auth-store. `hermes auth status` reports logged in, but `auxiliary.compression.provider: xai-oauth` previously fell through to "No auxiliary LLM provider configured".

Root cause: `_resolve_xai_oauth_for_aux()` only called `resolve_xai_oauth_runtime_credentials()`, which reads `auth.json` singleton state and raises `AuthError` for pool-only logins — swallowed by bare try/except → returned `None`.

## Changes
- `agent/auxiliary_client.py`: try `load_pool("xai-oauth")` first, mirroring the main runtime path in `runtime_provider.py` (`runtime_api_key or access_token`, env→pool→default base_url precedence). Fall back to singleton resolver for older auth-store-only logins.
- `run_agent.py`: when an explicit aux compression provider is configured but unavailable, the preflight warning now names that provider instead of suggesting `OPENROUTER_API_KEY`.
- `tests/agent/test_auxiliary_client.py`: 2 regression tests covering pool-only credentials and `HERMES_XAI_BASE_URL` override.

## Validation
- `scripts/run_tests.sh tests/agent/test_auxiliary_client.py::TestResolveXaiOAuthForAux` → 2/2 passed.

Credit: @helix4u (commit authorship preserved via cherry-pick).
.