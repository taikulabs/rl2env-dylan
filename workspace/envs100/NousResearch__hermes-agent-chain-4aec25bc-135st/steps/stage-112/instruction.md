**feat(kanban): stale detection for running tasks in dispatcher**

Salvages #23790 by @thewillhuang.

Adds `detect_stale_running()` to the dispatcher cycle. Running tasks started for longer than `dispatch_stale_timeout_seconds` (default 14400 = 4h) without a heartbeat in the last hour are auto-reclaimed to `ready`.

- New config `kanban.dispatch_stale_timeout_seconds` (default 14400, 0 disables)
- New `stale` field on `DispatchResult`
- `detect_stale_running()` checks running-status tasks with heartbeat freshness
- Records `outcome='stale'` on run close + `stale` event; ticks failure counter
- Wires config through gateway embedded dispatcher
- Updates `_cmd_dispatch` verbose/JSON output and daemon logging

Resolved test-file end-of-file conflict by appending both halves. Authorship preserved via rebase merge.

## Validation
- 11 stale-related tests pass.