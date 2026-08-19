**fix(profiles): detect a separate-process gateway in profile status**

## Infographic

![gateway-status-fixed](https://v3b.fal.media/files/b/0a9f8ba6/NTvmKRjMpvd3Fgxw78Cn8_MLAGMelD.png)

## Summary

The dashboard **Profiles** view shows **"Gateway stopped"** for a gateway that is in fact running, while the **sidebar** status strip *and* `hermes gateway status` (CLI) both correctly report it **running**. Reported on **v0.17.0** with the gateway + dashboard running in a single Docker container:

```
$ hermes gateway status
✓ Gateway is running (PID: 134)
  (Running manually, not as a system service)
```

## Root cause

Three liveness surfaces, three detection strengths — all reading the same `gateway.pid` under `$HERMES_HOME`:

| Surface | Detector | Result |
|---|---|---|
| `hermes gateway status` (CLI) | `find_gateway_pids()` — process-table scan | ✅ running |
| Sidebar `/api/status` | `get_running_pid()` **+ `gateway_state.json` PID fallback + health-URL probe** | ✅ running |
| **Profiles view** | `_check_gateway_running()` = `get_running_pid()` **only, no fallback** | ❌ stopped |

`get_running_pid()` (`gateway/status.py`) short-circuits to `None` the moment the runtime lock (`gateway.lock`) doesn't register as held by the *calling* process — **before** it inspects the PID record. That's always the case when the reader is a **separate process** from the gateway (in the container the dashboard is its own s6 service), and also for any launch-service-managed gateway that left a fresh `gateway_state.json` but no live PID file. So the Profiles view alone reported the live gateway as stopped.

## Fix

Give `_check_gateway_running()` the same fallback the sidebar already has (`web_server.py:1854`): after the pid-file/lock check misses, validate the PID recorded in **that profile's** `gateway_state.json` against the live process table via the existing `get_runtime_status_running_pid()`.

`read_runtime_status()` gains an optional `path` argument so a specific profile's state file can be read **without mutating the process-global `HERMES_HOME`** — preserving the contextvar-based profile isolation the dashboard relies on, and avoiding the env-mutation race an earlier approach would have introduced. The fallback is also strictly stronger than `#20488`'s `service_running`-only check, which is always `False` in Docker (no systemd/launchd) and would still miss PID 134.

**Backward compatible:** every existing caller of `read_runtime_status()` passes no argument.

## Tests

- `test_gateway_running_check_falls_back_to_runtime_state` — live gateway, pid-file/lock check returns `None`, must still report running. **Verified failing on baseline, passing with the fix.**
- `test_gateway_running_check_runtime_state_stopped` — a `gateway_state.json` with state `stopped` is never reported running, even with a live recorded PID.

`tests/hermes_cli/test_profiles.py` (140) + the gateway runtime-status suites all pass.

---

🎨 *Infographic is decorative — details are illustrative, not a spec.*