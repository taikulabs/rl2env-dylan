**fix(codex-oauth): quarantine terminal refresh errors so dead tokens are not replayed across sessions**

Salvage of #27911 by @EloquentBrush0x. Contributor's branch was severely stale (would have reverted ~5000 LOC across azure/kanban/i18n subsystems). Fix re-applied surgically on current main with their predicate, quarantine pattern, and tests preserved.

## Summary
Mirrors the just-landed xAI quarantine and the existing Nous quarantine (c90556262) for codex-oauth: when a Codex refresh token is permanently invalidated, clear it from auth.json so the next session doesn't re-seed the dead token. Also adds a pre-refresh sync to close the same single-use refresh-token race that xAI and Nous already close.

## Changes
- `hermes_cli/auth.py`: `_is_terminal_codex_oauth_refresh_error` predicate matching codex error codes (codex_refresh_failed, codex_auth_missing_refresh_token, invalid_grant, invalid_token, refresh_token_reused) with relogin_required gate
- `agent/credential_pool.py`: pre-refresh sync on codex elif branch + race-recovery + terminal quarantine block in exception handler. Removes `device_code`-sourced entries (preserves manual API keys), writes `last_auth_error` diagnostic blob, persists pool.
- `tests/agent/test_credential_pool.py`: 3 tests (predicate precision, end-to-end happy path with manual-entry survival, negative case for transient errors)

## Validation
`scripts/run_tests.sh tests/agent/test_credential_pool.py` → 52/52 passing.

 (salvage merge — contributor authorship preserved via --author flag).