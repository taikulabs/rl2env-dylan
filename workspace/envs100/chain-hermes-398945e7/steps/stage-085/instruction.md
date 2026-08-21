**fix(gateway): shutdown + restart hygiene (drain timeout, false-fatal, success log)**

## Summary
Gateway shutdowns and restarts stop emitting false-positive error/success lines, and /restart no longer force-interrupts mid-API-call agents under realistic conversation loads.

Three issues from a real restart chain on 2026-05-02 (three cascading restarts in the user's gateway.log), all fixed here.

## Changes

- **`gateway/run.py`** — `_send_restart_notification()` now inspects `result.success` before logging. Previously logged `Sent restart notification to <chat>` at INFO unconditionally, even when `adapter.send()` returned `SendResult(success=False)` (e.g. Telegram 'Chat not found'). Failures now log WARNING with the underlying error.
- **`gateway/platforms/whatsapp.py`** — `disconnect()` sets `self._shutting_down = True` before SIGTERMing the bridge; `_check_managed_bridge_exit()` returns None for `returncode in (0, -2, -15)` while shutting down. Previously every planned shutdown logged `ERROR ... WhatsApp bridge process exited unexpectedly (code -15)` plus `Fatal whatsapp adapter error (whatsapp_bridge_exited)` just before `✓ whatsapp disconnected`. OOM-kill (137) and other abnormal exits still hit the fatal path.
- **`hermes_cli/config.py`** — `agent.restart_drain_timeout` default 60 → 180. A real `/restart` on 2026-05-02 01:43:27 interrupted three agents with 82s/112s/154s in-flight API calls because the 60s budget expired. Explicit user values in `config.yaml` are preserved by deep-merge.

## Validation

| | Before | After |
|---|---|---|
| Restart notification fail | INFO 'Sent restart notification to …' (lie) | WARNING 'Restart notification to … was not delivered: Chat not found' |
| WhatsApp planned shutdown | ERROR 'bridge process exited unexpectedly' + 'Fatal whatsapp adapter error' | INFO 'Bridge exited during shutdown (code -15)' |
| WhatsApp real crash during shutdown | ERROR + fatal path | unchanged (still ERROR + fatal for returncodes outside {0,-2,-15}) |
| /restart with 3 active agents | drain timed out at 60s, all interrupted | 180s drain — typical conversations finish |
| Explicit user `restart_drain_timeout: 45` | 45 | 45 (unchanged) |

Targeted tests: 139/139 pass (tests/gateway/test_restart_notification.py, tests/gateway/test_restart_drain.py, tests/hermes_cli/test_gateway_service.py, the 4 relevant TestBridgeRuntimeFailure cases).

E2E: isolated `HERMES_HOME` verified all four config paths (default new install = 180, explicit user value preserved = 45, DEFAULT_CONFIG exports 180, DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT = 180.0).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_config_env_bridge_authority.py`
- `tests/gateway/test_restart_notification.py`
- `tests/gateway/test_whatsapp_connect.py`
- `tests/hermes_cli/test_setup_agent_settings.py`