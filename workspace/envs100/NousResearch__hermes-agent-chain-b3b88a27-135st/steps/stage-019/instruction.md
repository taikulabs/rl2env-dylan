**fix(google-workspace): normalize authorized user token writes**

## Summary
Normalizes freshly written Google Workspace tokens to include `"type": "authorized_user"` so the `gws` CLI backend accepts them immediately after OAuth setup.

. 

## What changed
- Added `_normalize_authorized_user_payload()` helper to `setup.py`, `google_api.py`, and `gws_bridge.py`
- Applied normalization at all 4 token write points:
  - `exchange_auth_code()` — initial token write after OAuth
  - `check_auth()` — token refresh in setup script
  - `get_credentials()` — token refresh in API script
  - `refresh_token()` — gws bridge refresh
- Added tests verifying `"type"` field is persisted

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/skills/test_google_oauth_setup.py`
- `tests/skills/test_google_workspace_api.py`