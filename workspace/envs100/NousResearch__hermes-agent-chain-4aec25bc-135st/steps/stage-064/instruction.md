**fix(xai-oauth): quarantine terminal refresh errors so dead tokens are not replayed across sessions**

Salvage of #27898 by @EloquentBrush0x cherry-picked onto current main.

## Summary
Parity gap: Nous OAuth already quarantines dead refresh tokens (terminal HTTP 400/401/403 from refresh) so they're cleared from auth.json and not re-seeded into the pool next session (added in c90556262). xAI-oauth had no such path — a single revoked or refresh-token-reused error would leave the dead token on disk, get re-seeded on every `load_pool()`, and silently 401 every subsequent agent. Plausibly the root cause of the 'x_search tool not loading' class of community reports.

## Changes
- `hermes_cli/auth.py`: `_is_terminal_xai_oauth_refresh_error` predicate (provider + code + relogin_required gate)
- `agent/credential_pool.py`: quarantine block in `_refresh_entry` xAI path — clears tokens from auth.json under lock + store_refresh==entry_refresh guard, writes structured `last_auth_error`, removes loopback_pkce entries (preserves manual ones), resets `_current_id`, persists pool. Mirrors the Nous pattern.
- `tests/agent/test_credential_pool.py`: 3 tests covering predicate precision, end-to-end happy path, and negative case (429/5xx must NOT quarantine).

## Validation
`scripts/run_tests.sh tests/agent/test_credential_pool.py` → 49/49 passing.

 (salvage merge — author preserved).