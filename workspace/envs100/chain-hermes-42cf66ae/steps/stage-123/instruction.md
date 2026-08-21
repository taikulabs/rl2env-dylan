**fix(setup+gateway): defer config write, PID-based gateway kill, scoped systemd service names**

## Summary

Three related setup/gateway fixes for multi-install safety:

### 1. Defer config.yaml write until after model selection (setup.py)

`_update_config_for_provider()` was called before model selection, creating a race where the gateway picks up a new provider with the old model. Now deferred to right before `save_config()`.

### 2. Kill gateway via PID file before restart on update (main.py)

`hermes update` only ran `systemctl restart`, leaving manually-started gateways alive (duplicates). Now uses `get_running_pid()` (scoped to HERMES_HOME) to SIGTERM this installation's gateway first.

Based on PR #1131 by @teknium1.

### 3. Scope systemd service name to HERMES_HOME (NEW)

Multiple installations on the same machine now get unique systemd service names:
- Default `~/.hermes` → `hermes-gateway` (backward compatible)
- Custom HERMES_HOME → `hermes-gateway-<8-char-hash>`

`get_service_name()` derives a deterministic name via SHA256 of the resolved HERMES_HOME path. All systemd references across `gateway.py`, `main.py`, `status.py`, and `uninstall.py` now use it.

The systemd unit template also now sets `Environment="HERMES_HOME=..."` so the gateway process knows which installation it belongs to.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_gateway.py`
- `tests/hermes_cli/test_gateway_linger.py`
- `tests/hermes_cli/test_gateway_service.py`