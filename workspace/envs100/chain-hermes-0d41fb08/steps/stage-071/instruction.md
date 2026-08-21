**fix(api-server): share one Docker container across all API conversations**

## Summary

Fixes the bug where the API server (used by Open WebUI) created a new Docker container for every single message, making it unusable for any multi-step work.

**Root cause:** `_run_agent()` never passed `task_id` to `run_conversation()`, so each request generated a fresh random UUID. The terminal tool keyed containers by task_id, meaning every message got its own ephemeral sandbox.

**Fix:**
1. Pass `task_id="default"` from both `_run_agent()` and the `/v1/runs` endpoint — all API server conversations now share the same Docker container, matching the design intent (one configured Docker environment = one container)
2. Derive a stable `session_id` from a hash of the system prompt + first user message, so `hermes sessions list` isn't polluted with single-message throwaway sessions

**What this means for users:**
- Docker container persists across messages — files, installed packages, and working directory state survive between turns
- Session list stays clean
- `X-Hermes-Session-Id` header still works for explicit session control (unchanged)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`