**fix: detect copilot and qwen-oauth providers in /model picker**

## Summary

Fixes two gaps in `/model` provider detection where providers with dynamic credential resolution weren't being detected by `list_authenticated_providers()`.

**Copilot** (

**Qwen OAuth** (new): Same gap pattern. Users authenticating via `qwen auth qwen-oauth` store tokens in `~/.qwen/oauth_creds.json`. The runtime resolver reads this file, but the credential pool had no handler for it. Seeds qwen-oauth credentials from `resolve_qwen_runtime_credentials(refresh_if_expiring=False)` to avoid network calls during discovery.

Both follow the existing pattern established by anthropic, nous, and openai-codex seeding.

## Changes

- `agent/credential_pool.py` — Add copilot and qwen-oauth branches in `_seed_from_singletons()`
- `tests/agent/test_credential_pool.py` — 4 new tests (2 per provider: token found → seeded, no token → empty)