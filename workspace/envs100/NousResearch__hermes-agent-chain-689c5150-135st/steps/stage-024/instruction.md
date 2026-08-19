**fix: write update exit code before gateway restart (cgroup kill race)**

## Summary

Fixes the spurious "❌ Hermes update timed out after 30 minutes" message that appears after a successful `/update` via Telegram.

## Root Cause

When `/update` is triggered from the gateway, `hermes update --gateway` is spawned as a child of the gateway process. Despite using `setsid` for session isolation, the child process inherits the gateway's **systemd cgroup**. The service template uses `KillMode=mixed`, so when the update process calls `systemctl restart hermes-gateway`:

1. systemd sends SIGTERM to the gateway main process
2. When the main process exits, systemd sends **SIGKILL to all remaining processes in the cgroup**
3. This kills both `hermes update --gateway` and its wrapping bash shell
4. The shell epilogue (`printf $status > .update_exit_code`) never executes
5. The new gateway boots, starts a fresh update watcher
6. The watcher polls for 30 minutes, never finds the exit code → timeout message

The user sees the streamed "✓ Update complete!" text (printed before the restart attempt) and then the spurious timeout 30 minutes later.

## Fix

Write `.update_exit_code` from Python inside `cmd_update()` immediately after git pull + pip install succeed, **before** attempting the gateway restart. Only done in `--gateway` mode (normal CLI updates still rely on the shell epilogue).

The shell epilogue still writes the file too (idempotent overwrite with the same value), but now the marker exists even when the process is killed mid-restart.

## Tests

3 new tests in `test_update_gateway_restart.py`:
- `test_exit_code_written_in_gateway_mode` — verifies marker is created
- `test_exit_code_not_written_in_normal_mode` — no side effects for CLI usage
- `test_exit_code_written_before_restart_call` — verifies ordering: exit code exists before `systemctl restart` is called

All 34 tests in the file pass.

## Files Changed

- `hermes_cli/main.py` — +20 lines (write exit code before restart block)
- `tests/hermes_cli/test_update_gateway_restart.py` — +117 lines (3 new tests)