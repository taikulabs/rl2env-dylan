**fix(gateway): add HERMES_SESSION_KEY to session_context contextvars**

## Summary

Completes the contextvars migration from e8034e2f by adding `HERMES_SESSION_KEY` to the unified `_VAR_MAP` in `session_context.py`. Without this, concurrent gateway handlers race on `os.environ["HERMES_SESSION_KEY"]` — handler A can read handler B's session key.

## Changes

- **`gateway/session_context.py`**: Add `_SESSION_KEY` ContextVar to `_VAR_MAP`, add `session_key` param to `set_session_vars()` / `clear_session_vars()`
- **`gateway/run.py`**: Pass `context.session_key` through `_set_session_env()` (kept `os.environ` set as CLI/cron fallback)
- **`tools/approval.py`**: Replace `os.getenv` fallback with `get_session_env()` for unified resolution chain (approval contextvars → session_context contextvars → os.environ). Import is function-level to avoid tools→gateway module-level coupling.
- **`tests/gateway/test_session_env.py`**: 4 new tests covering SESSION_KEY contextvars, os.environ fallback, SessionContext propagation, and concurrent task isolation

## Test results

- `test_session_env.py`: 9/9 passed (5 existing + 4 new)
- Approval/command guard/yolo tests: 170/170 passed