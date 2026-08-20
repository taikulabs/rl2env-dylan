**fix(gateway): close adapter resources when connect() fails or raises**

## Summary
Adapter resources are released on every failure path, eliminating `Unclosed client session` warnings and leaked bridge/poll tasks when a platform fails to connect.

Before: if `adapter.connect()` returned False or raised, the adapter was never added to `self.adapters`, so the shutdown path never called `disconnect()` on it. Any `aiohttp.ClientSession` / poll task / child subprocess the adapter had already allocated leaked until Python GC logged `Unclosed client session` at process exit.

Observed on 2026-04-18 18:08:16 during a double `--replace` takeover cycle — one of the partial-init sessions survived past shutdown and emitted the warning right before `status=75/TEMPFAIL`.

## Changes
- `gateway/run.py`: new `GatewayRunner._safe_adapter_disconnect()` helper. Calls `adapter.disconnect()` and swallows any exception (callers are already on error paths).
- `gateway/run.py`: connect loop calls it in both failure branches (`success=False` and `except Exception`).
- `tests/gateway/test_safe_adapter_disconnect.py`: 3 regression tests.

## Validation
| | Before | After |
|---|---|---|
| `connect()` raises after allocating ClientSession | session leaked to GC | session closed |
| `connect()` returns False after allocating subprocess | subprocess orphaned | disconnect() cleans up |
| `adapter.disconnect()` itself raises | cleanup path broken | debug-logged, swallowed |
| `adapter.has_fatal_error` read after cleanup | (unchanged) | still correct — `_mark_disconnected()` preserves fatal-error state |

Targeted: `test_safe_adapter_disconnect.py` 3/3, `test_gateway_shutdown.py` 6/6, `test_command_bypass_active_session.py` 41/41, `test_steer.py` 18/18.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_safe_adapter_disconnect.py`