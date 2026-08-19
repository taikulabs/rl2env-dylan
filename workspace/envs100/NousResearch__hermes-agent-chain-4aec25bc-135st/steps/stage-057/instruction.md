**fix(azure-foundry): send Bearer auth to anthropic_messages, keep 1M beta (salvage #27022)**

Salvages @sharziki's #27022 and fixes a hidden side-effect.

## Summary
Azure AI Foundry's `/anthropic` endpoint requires `Authorization: Bearer` instead of `x-api-key`. Without this, requests return HTTP 401.

## Changes
- `agent/anthropic_adapter.py::_requires_bearer_auth` — add `azure.com` (sharziki's #27022).
- `agent/anthropic_adapter.py::_common_betas_for_base_url` — guard the beta-strip on a new `_is_minimax_anthropic_endpoint` predicate instead of `_requires_bearer_auth`. Otherwise, folding Azure into the bearer-auth branch silently triggered the MiniMax-specific strip of `fine-grained-tool-streaming` + `context-1m-2025-08-07`, killing the 1M context window on Azure Foundry.
- `tests/agent/test_anthropic_adapter.py` — regression test: Azure → `auth_token` (Bearer), `api-version` query param plumbing, and `context-1m-2025-08-07` survives.

## Validation
- `scripts/run_tests.sh tests/agent/` → 3073/3073 passing (no regressions).
- New test exercises the exact `azure.com` host shape end-to-end through `build_anthropic_client`.

## Credit
Cherry-picked @sharziki's commit on top of current main; the follow-up fix to keep the 1M beta is on top. Rebase-merge preserves their authorship.