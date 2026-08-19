**fix(copilot): fall back to credential_pool OAuth access_token for /model picker**

Salvage of #16868 (@briandevans) onto current main. Original branch was ~35 commits behind; cherry-picked cleanly with authorship preserved.

## Summary

Copilot `/model` picker now picks up the OAuth `gho_*` token that `hermes auth add copilot` writes to `auth.json`'s credential pool, instead of only looking at env vars / `gh auth token`. Device-code-only users were silently seeing a stale hardcoded Copilot model list (missing `claude-opus-4.7`, `gpt-5.5`, etc.) because `_resolve_copilot_catalog_api_key()` never consulted the pool. `/model <id>` worked because runtime inference reads the pool through a different path — only the catalog fetch was wedged.

## Changes

- `hermes_cli/models.py::_resolve_copilot_catalog_api_key` — env lookup first (unchanged). On miss, walk `read_credential_pool("copilot")`, reject classic `ghp_*` up-front via `validate_copilot_token`, run each candidate through `exchange_copilot_token` — only entries that actually exchange return a value, so an expired pool[0] doesn't wedge a later valid entry.
- Mirrors the Codex catalog resolver at `hermes_cli/models.py:1791`.
- `tests/hermes_cli/test_copilot_catalog_oauth_fallback.py` — 7 focused tests + skip-and-try-next regression (8 total after the follow-up commit).

## Why exchange, not raw access_token

`COPILOT_MODELS_URL` is `api.githubcopilot.com/models`, which requires the exchanged `tid_*` API token — not the raw `gho_*` OAuth token. The issue's proposed fix (return `access_token` directly) would still 401.

## Validation

- Targeted: 48/48 pass across `test_copilot_catalog_oauth_fallback`, `test_copilot_in_model_list`, `test_copilot_auth`, `test_copilot_token_exchange`.
- E2E with real imports + isolated `HERMES_HOME`:
  - env empty + pool `gho_*` → `_resolve_copilot_catalog_api_key()` returns exchanged `tid_*`; `provider_model_ids("copilot")` returns full list.
  - env set + pool populated → pool is never read (exchange called exactly once, for the env token).

. Supersedes #16868.