**fix(gateway): launchd_stop uses bootout so KeepAlive doesn't respawn**

## Summary

`hermes gateway stop` on macOS was a no-op — it sent SIGTERM via `launchctl kill`, but the plist's `KeepAlive.SuccessfulExit=false` immediately respawned the process. Users saw "✓ Service stopped" while the gateway kept running.

**Root cause of Discord report:** A user edited `~/.hermes/.env` and ran `hermes gateway stop && hermes gateway restart`, but the new env var wasn't picked up. The `stop` didn't actually stop anything — the respawned process loaded the old env, and `restart` then killed *that* process and started a new one (which should have loaded the new env, but the race made it unreliable).

## Changes

- **`launchd_stop()`**: Switch from `launchctl kill SIGTERM` to `launchctl bootout`, which unloads the service definition so KeepAlive can't trigger. The process exits and stays stopped.
- Adds `_wait_for_gateway_exit()` call after bootout to ensure the process is fully gone before returning.
- Tolerates 'already unloaded' error codes (3/113) gracefully.
- **No changes to `launchd_start()`** — it already handles re-bootstrapping unloaded jobs via its error code 3/113 fallback path.
- 3 new tests covering bootout behavior, already-unloaded tolerance, and exit wait.

## Compatibility

After `hermes gateway stop`, the service stays stopped until:
- `hermes gateway start` (re-bootstraps the plist)
- Next login/reboot (RunAtLoad in \~/Library/LaunchAgents/ auto-bootstraps)

This matches the expected behavior — `stop` should mean stopped.