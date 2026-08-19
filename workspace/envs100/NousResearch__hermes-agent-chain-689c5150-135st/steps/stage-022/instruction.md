**fix: write refreshed Codex tokens back to ~/.codex/auth.json**

## Summary

OpenAI OAuth refresh tokens are single-use and rotate on every refresh. When Hermes refreshes a Codex token, it consumed the old refresh_token but **never wrote the new pair back to `~/.codex/auth.json`**. This caused Codex CLI and VS Code to fail with `refresh_token_reused` on their next refresh attempt.

**Root cause:** The Anthropic path already had a write-back (`_write_claude_code_credentials()` → `~/.claude/.credentials.json`), but the Codex path was intentionally designed not to write back. That was the wrong call — when you consume a single-use token, you must update all consumers.

## Changes

- **`hermes_cli/auth.py`**: Add `_write_codex_cli_tokens()` — reads existing `~/.codex/auth.json`, updates tokens, writes back with 0600 permissions. Mirrors `_write_claude_code_credentials()` pattern.
- **`hermes_cli/auth.py`**: Call write-back from `_refresh_codex_auth_tokens()` (non-pool refresh path)
- **`agent/credential_pool.py`**: Call write-back from `_refresh_entry()` happy path and retry path
- **Tests**: 4 new tests for write-back behavior, updated existing test docstring

## Write-back points (3 total)

1. `_refresh_codex_auth_tokens()` — non-pool singleton refresh (e.g., `resolve_codex_runtime_credentials(force_refresh=True)`)
2. `CredentialPool._refresh_entry()` — pool happy path after successful refresh
3. `CredentialPool._refresh_entry()` — pool retry path (when CLI consumed the token between sync and refresh)

## E2E verified

Tested with isolated HERMES_HOME + CODEX_HOME: after Hermes refreshes a token, both `~/.hermes/auth.json` and `~/.codex/auth.json` contain the fresh pair. File permissions verified at 0600.

Fixes refresh token conflict reported by @ec12edfae2cb221