**fix(minimax-oauth): quarantine dead tokens on terminal refresh failure**

Salvage of #28003 by @EloquentBrush0x. Contributor's branch was severely stale (would have reverted ~5000 LOC across azure/kanban/i18n). Fix re-applied surgically on current main with their quarantine pattern preserved, plus two new regression tests (which the original PR was missing).

## Summary
Completes the OAuth quarantine parity sweep: Nous (existing), xAI, Codex, MiniMax (this). When MiniMax OAuth refresh raises with `relogin_required=True`, clear the dead tokens from auth.json so the next call fails fast with not_logged_in instead of replaying the dead refresh_token over the network.

## Changes
- `hermes_cli/auth.py`: wrap `_refresh_minimax_oauth_state` in resolve_minimax_oauth_runtime_credentials with try/except; on terminal failure, clear access_token/refresh_token/expires_*/obtained_at, write structured `last_auth_error`, persist via `_minimax_save_auth_state`, re-raise.
- `tests/test_minimax_oauth.py`: 2 new tests (terminal-failure quarantines + transient-failure does NOT quarantine).

## Validation
`scripts/run_tests.sh tests/test_minimax_oauth.py` → 21/21 passing.

 (salvage merge — contributor authorship preserved).