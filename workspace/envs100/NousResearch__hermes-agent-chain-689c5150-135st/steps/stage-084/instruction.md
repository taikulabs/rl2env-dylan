**fix: hermes gateway restart waits for service to come back up**

## Summary

 — `hermes gateway restart` returned immediately after sending SIGUSR1, while the gateway was still draining/restarting. Users saw "restart requested" but the service was down for 30-60 seconds with no feedback.

### Before
```
$ hermes gateway restart
✓ User service restart requested     ← returns immediately, service still dying
$ hermes gateway status
✗ User gateway service is stopped    ← surprise
```

### After
```
$ hermes gateway restart
⏳ User service draining active work...
⏳ Waiting for hermes-gateway to restart...
✓ User service restarted (PID 12345)    ← blocks until actually up
```

Or on timeout:
```
⚠ User service did not become active within 60s.
  Check status: hermes gateway status
  Check logs: journalctl --user -u hermes-gateway --since '2 min ago'
```

### Implementation

Two-phase wait after sending SIGUSR1:

1. **Phase 1 (up to 90s)**: Poll `os.kill(pid, 0)` until old process is dead
2. **Phase 2 (up to 60s)**: Poll `systemctl is-active` + verify new PID via `get_running_pid()`

The `reload-or-restart` fallback path is already synchronous (systemctl blocks), so no changes needed there.