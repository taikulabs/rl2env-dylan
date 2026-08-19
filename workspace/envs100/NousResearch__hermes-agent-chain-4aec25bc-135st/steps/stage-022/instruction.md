**fix(codex): rotate pool on usage_limit_reached 429**

Salvage of #26390 onto current main. Preserves @Qwinty's authorship.

## Summary
Codex HTTP 429 with `error.type = "usage_limit_reached"` now rotates the credential pool immediately instead of wasting one retry against the exhausted OAuth profile.

Root cause: `_extract_api_error_context()` ignored `payload["type"]`, so the classifier saw a generic transient 429 and intentionally retried the same credential once before rotating.

## Changes
- `run_agent.py`: `_extract_api_error_context()` now reads `payload["type"]` as a reason fallback.
- `run_agent.py`: `_recover_with_credential_pool()` skips the first-retry-same-credential branch when reason/message indicates `usage_limit_reached`.
- `tests/run_agent/test_run_agent.py`: regression coverage for both behaviors.

## Validation
- `scripts/run_tests.sh tests/run_agent/test_run_agent.py::TestCredentialPoolRecovery -q` → 10/10 passed.
- `scripts/run_tests.sh tests/run_agent/test_run_agent.py tests/agent/test_credential_pool.py -q` → 374/374 passed.

. Original PR #26390.