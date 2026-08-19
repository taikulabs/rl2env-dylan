**fix(setup): validate base URL input in hermes model flow**

## Summary

Adds URL validation to the base URL prompt in `_model_flow_api_key_provider()` (the generic setup flow for Z.AI, MiniMax, DeepSeek, etc.). Rejects values that don't start with `http://` or `https://` with a clear error message instead of saving garbage to `.env`.

## Motivation

A non-dev user in Discord accidentally typed `nano ~/.hermes/.env` into the base URL prompt during Z.AI setup, intending to open the file for editing. It got saved as `GLM_BASE_URL=nano ~/.hermes/.env`, which then caused every API connection attempt to fail with DNS resolution errors. The user spent hours trying to debug what looked like a network issue.

The custom-endpoint flow (line 1620) already had this validation — this brings the generic API-key provider flow to parity.

## Changes

- **`hermes_cli/main.py`** — Added `startswith(("http://", "https://"))` check before saving base URL override
- **`tests/hermes_cli/test_model_provider_persistence.py`** — 3 new tests: invalid URL rejected, valid URL accepted, empty input preserves default