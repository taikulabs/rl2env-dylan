**fix(xai-oauth): quarantine dead tokens in direct-resolve path**

Salvage of #28171 (@EloquentBrush0x).

## Summary
Closes the parity gap in the xAI OAuth quarantine: the pool path (`credential_pool.py`, landed in 5e40f83cb) clears dead tokens on terminal refresh failure, but the direct-resolve path `resolve_xai_oauth_runtime_credentials()` still called `_refresh_xai_oauth_tokens` with no try/except — so HTTP 400/401/403 (`invalid_grant`, token revoked) propagated, leaving dead tokens in `auth.json` to be replayed on every subsequent process start.

## Changes
- `hermes_cli/auth.py`: wrap the refresh call; on terminal error (`_is_terminal_xai_oauth_refresh_error`), clear `access_token`/`refresh_token` from auth.json and write a `last_auth_error` diagnostic marker. `active_provider` preserved (`set_active=False`).
- `tests/hermes_cli/test_auth_xai_oauth_provider.py`: terminal-failure quarantine test + transient-failure non-quarantine test.

## Validation
- `scripts/run_tests.sh tests/hermes_cli/test_auth_xai_oauth_provider.py -q` → 70/70 passing.

Authorship preserved via cherry-pick.