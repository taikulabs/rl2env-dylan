**fix(gateway): use setsid instead of systemd-run --user for /update (salvage #4024)**

## Summary

Salvaged from PR #4024 by @Sertug17. .

`/update` via Telegram silently failed when the gateway ran under a system-level systemd service. `systemd-run --user --scope` requires a user D-Bus session which is unavailable in system service context — the pending file was written but `hermes update` never executed.

Replace with `setsid` which creates a new detached session portably, without requiring D-Bus. Falls back to `start_new_session=True` on systems without the setsid binary (e.g. macOS, minimal containers).

## Changes

- `gateway/run.py`: Replaced `systemd-run --user --scope` with `setsid` in `_handle_update_command()`
- `tests/gateway/test_update_command.py`: Updated 3 tests to match new setsid behavior

## Test Results

- All 25 update command tests pass
- Full suite (7,060 tests): 7 pre-existing failures unrelated to this change, 0 new failures
- E2E verified: setsid + start_new_session=True produces PPID=1 (reparented to init), providing maximum process isolation
- Simulated real scenario: update child survives gateway SIGTERM and completes successfully