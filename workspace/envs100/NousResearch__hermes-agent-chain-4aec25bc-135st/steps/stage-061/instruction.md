**fix(error_classifier): classify xAI Grok entitlement SSE errors as auth, not retryable**

Salvage of #27429 by @EloquentBrush0x cherry-picked onto current main.

## Summary
xAI Responses SSE `type=error` frames carrying grok-subscription/quota messages were falling through to `FailoverReason.unknown` and burning the full retry budget before failing over. Now classified as auth (non-retryable), matching the HTTP-403 entitlement path.

## Changes
- `agent/error_classifier.py`: add two precise patterns matching "do not have an active grok subscription" and "out of available resources" + "grok", returning `FailoverReason.auth`
- `tests/run_agent/test_codex_xai_oauth_recovery.py`: 3 new tests (positive matches + negative case)

## Validation
`scripts/run_tests.sh tests/run_agent/test_codex_xai_oauth_recovery.py` → 25/25 passing.

 (salvage merge — author preserved).