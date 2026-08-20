**feat: API server model name derived from profile name**

## Summary

For multi-user setups (e.g. OpenWebUI), each profile's API server now advertises a distinct model name on `/v1/models` instead of the hardcoded `hermes-agent`.

**Behavior:**
- Profile `lucas` → model ID `lucas`
- Profile `admin` → model ID `admin`
- Default profile → `hermes-agent` (unchanged, backward-compatible)

**Explicit override:** `API_SERVER_MODEL_NAME` env var or `platforms.api_server.model_name` config for custom names.

## Context

Discord user Lucas_vw runs multiple profiles with OpenWebUI as frontend. OpenWebUI aggregates model names from all connections into one dropdown — when all connections advertise `hermes-agent`, they're indistinguishable. This change makes each profile naturally distinct with zero config.

## Changes

| File | Change |
|------|--------|
| `gateway/platforms/api_server.py` | Added `_resolve_model_name()` static method; replaced 4 hardcoded `hermes-agent` model name refs with `self._model_name`; log model name at startup |
| `gateway/config.py` | Plumbed `API_SERVER_MODEL_NAME` env var into platform extra config |
| `hermes_cli/config.py` | Added `API_SERVER_MODEL_NAME` to `OPTIONAL_ENV_VARS` |
| `tests/gateway/test_api_server.py` | 5 new tests: profile resolution, explicit override, default fallback |

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`