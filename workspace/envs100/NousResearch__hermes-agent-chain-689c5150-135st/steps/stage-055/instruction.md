**fix: dashboard shows Nous Portal as 'not connected' despite active auth**

## Summary

Fixes the bug where the dashboard Keys tab shows Nous Portal as "not connected" even when the backend is fully authenticated and working.

**Root cause:** The dashboard's device-code flow (`_nous_poller` in `web_server.py`) saved credentials to the **credential pool** only, but `get_nous_auth_status()` only checked the **auth store** (`auth.json`). The inference path worked because `resolve_runtime_provider()` checks the credential pool, but the status display didn't.

## Changes

**`hermes_cli/auth.py`** — `get_nous_auth_status()` now checks the credential pool first (matching `get_codex_auth_status()`'s existing pattern), then falls back to the auth store.

**`hermes_cli/web_server.py`** — `_nous_poller()` now also persists to the auth store after saving to the credential pool, matching what the CLI flow (`_login_nous`) does.

**`tests/hermes_cli/test_auth_nous_provider.py`** — 3 new tests:
- Pool-only credentials → `logged_in: True`
- Auth-store fallback when pool is empty → `logged_in: True`
- Both empty → `logged_in: False`