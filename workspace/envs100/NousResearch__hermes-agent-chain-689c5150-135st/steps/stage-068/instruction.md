**fix: resolve CI test failures — add missing functions, fix stale tests**

## Summary

Comprehensive CI fix addressing **27 test failures + 57 test errors** on current main.

### Production code fixes (4 files)

| File | Fix |
|------|-----|
| `hermes_logging.py` | Add `clear_session_context()` — referenced in docstring and tests but never implemented (48 teardown errors) |
| `tools/approval.py` | Add `clear_session()` — was removed but tests still reference it (9 setup errors) |
| `gateway/platforms/matrix.py` | Add SyncError `M_UNKNOWN_TOKEN` check in `_sync_loop` — nio returns error objects (not exceptions) for auth failures, loop retried forever |
| `hermes_cli/runtime_provider.py` | Fall back to inline `api_key` in named custom providers when `key_env` is absent — users who put API keys directly in the providers dict had them silently ignored |

### Test fixes (13 files)

All failures were stale tests — production code evolved and tests weren't updated. Key patterns:
- Missing attributes on `__new__`-constructed mock objects (`_execution_thread_id`, `_pending_megolm`, `model`/`provider`/etc.)
- Tests importing non-existent functions/modules (`get_vision_auxiliary_client`, `builtin_memory_provider`, `get_effective_display`)
- Token values not matching OAuth detection patterns (`_is_oauth_token` checks for `sk-ant-` or `eyJ` prefix)
- CI env var leakage (ANTHROPIC_API_KEY from GitHub secrets, INVOCATION_ID from systemd)
- pytest-xdist contextvar bleed between workers

### Verification

All 27 original CI failures + 57 errors resolved. Remaining 19 local-only failures are environment-dependent (pass in CI with `.[all,dev]` installed and blanked API keys).

Fixes #CI