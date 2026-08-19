**fix(gateway): handle stale lock files in acquire_scoped_lock**

Salvage of #8892 by @WorldInnovationsDepartment — cherry-picked onto current main.

## What this fixes

Empty or corrupt lock files (from a crash between `O_CREAT|O_EXCL` and `json.dump()`) permanently block `acquire_scoped_lock()`. Slack (or any platform) cannot reconnect even after gateway restart.

The fix unlinks the stale file when it exists on disk but `_read_json_file()` returns `None`, mirroring the existing dead-PID cleanup pattern.

## Changes
- `gateway/status.py` — 9 lines: unlink empty/corrupt lock files before `O_CREAT|O_EXCL`
- `tests/gateway/test_status.py` — 2 tests: empty file + corrupt JSON recovery

## Test results
- 14/14 `test_status.py` tests pass (12 existing + 2 new)
- E2E verified: empty file, corrupt JSON, normal lock regression, full Slack deadlock scenario