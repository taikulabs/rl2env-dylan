**fix: block agent from self-destructing gateway via terminal**

## Summary

 — agents running `hermes gateway restart`, `hermes update`, or `systemctl restart hermes-gateway` via the terminal tool kill the gateway process mid-work. Users see the agent suddenly stop responding.

### Changes

**tools/approval.py** (+8/-2):
- Added `hermes gateway stop/restart` pattern — requires approval
- Added `hermes update` pattern — requires approval (triggers gateway restart)
- Extended `systemctl` pattern to match flags between command and action: `systemctl --user restart` was previously undetected because the regex expected the action immediately after `systemctl`
- `restart` added to the existing `stop|disable|mask` systemctl pattern

**tests/tools/test_approval.py** (+2/-2):
- Updated `test_systemctl_restart_not_flagged` → `test_systemctl_restart_flagged` (intentional behavior change)

### What gets blocked vs allowed

| Command | Blocked? | Why |
|---------|----------|-----|
| `hermes gateway restart` | ✓ Requires approval | Kills running agents |
| `hermes gateway stop` | ✓ Requires approval | Kills running agents |
| `hermes update` | ✓ Requires approval | Restarts gateway |
| `systemctl restart hermes-gateway` | ✓ Requires approval | Kills running agents |
| `systemctl --user restart hermes-gateway` | ✓ Requires approval | Kills running agents |
| `hermes gateway status` | Safe | Read-only |
| `hermes gateway setup` | Safe | Configuration only |
| `systemctl status hermes-gateway` | Safe | Read-only |

In YOLO mode, these commands still execute without approval (by design).