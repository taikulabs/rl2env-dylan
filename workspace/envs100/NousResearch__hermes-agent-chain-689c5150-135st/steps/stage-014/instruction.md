**fix: openai-codex and anthropic not appearing in /model picker for external credentials**

## Summary

The `/model` picker wasn't detecting providers whose credentials live in external files rather than env vars or the Hermes auth store:
- **openai-codex** — OAuth tokens in `~/.codex/auth.json` (Codex CLI shared file)
- **anthropic** — Claude Code credentials in `~/.claude/.credentials.json`

Users saw these providers in `hermes auth` and `hermes model` (which use different detection paths) but not in the `/model` picker.

## Root Cause

`list_authenticated_providers()` had two gaps:

1. **Only checked the raw Hermes auth store** — didn't know about the Codex CLI fallback import (`~/.codex/auth.json` → Hermes auth store migration)
2. **Auth store/pool checks were gated behind `auth_type == oauth*`** — anthropic has `auth_type=api_key` in its overlay (it supports both), so the auth store and credential pool checks were never reached

## Fix (3 parts)

**`agent/credential_pool.py`** — `_seed_from_singletons()` for openai-codex now falls back to importing from `~/.codex/auth.json` when the Hermes auth store has no tokens. Mirrors the existing logic in `resolve_codex_runtime_credentials()`.

**`hermes_cli/model_switch.py`** — Two changes:
1. Auth store + credential pool checks now run for **all** providers, not just those with OAuth auth_type. This catches anthropic (api_key auth_type but also has OAuth credential files).
2. Direct check for anthropic external credential files (Claude Code, Hermes PKCE) bypassing the `is_provider_explicitly_configured()` gate. That gate is correct for runtime (don't burn tokens on auxiliary tasks without consent) but wrong for discovery (`/model` is explicitly about "what can I switch to?").

## Coverage Audit

Verified all provider types are now detected:
| Credential source | Providers | Detection path |
|---|---|---|
| Env vars (API keys) | openrouter, anthropic, zai, deepseek, etc. | Section 1 (models.dev) + Section 2 (HERMES_OVERLAYS) |
| Hermes auth store (OAuth) | nous, openai-codex, qwen-oauth, copilot-acp | Section 2 auth store check |
| Codex CLI file (`~/.codex/`) | openai-codex | **NEW** — pool auto-import fallback |
| Claude Code file (`~/.claude/`) | anthropic | **NEW** — direct file check |
| User-defined endpoints | custom | Section 3 (config.yaml `providers:`) |
| Saved custom providers | custom | Section 4 (config.yaml `custom_providers:`) |

## Tests
- 5 new regression tests (Codex CLI detection, migration, normal path, Claude Code detection, no-credentials negative)
- 38 existing related tests pass (overlay slug resolution, credential pool, model picker)