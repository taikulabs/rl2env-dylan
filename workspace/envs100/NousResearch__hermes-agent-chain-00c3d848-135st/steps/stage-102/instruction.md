**fix(cli): warn about stale dashboard processes after hermes update**

Salvages #16881 (@Societus) with a follow-up tightening commit.

## What this PR does
After `hermes update` finishes (both git and zip paths), scans the process table for running `hermes dashboard` processes and prints a warning with PIDs + restart instructions.

## Why
v0.11.0 added `X-Hermes-Session-Token`. A dashboard process started before the update keeps the old Python backend in memory while the JS bundle on disk gets replaced — the new frontend sends headers the stale backend doesn't recognize, so every API call returns 401 with no visible error (HTML loads, all data empty). .

The dashboard has no service manager (unlike the gateway, which systemd/launchd auto-restart), so we can only warn — not auto-kill.

## Changes
- **`hermes_cli/main.py`**: new `_warn_stale_dashboard_processes()` called from `_cmd_update_impl` (git path) and `_update_via_zip` (zip path). Cross-platform: `ps` on Linux/macOS, `wmic` on Windows. Excludes self-PID. Swallows `FileNotFoundError`/`TimeoutExpired`/`OSError`.
- **`tests/hermes_cli/test_update_stale_dashboard.py`**: 10 unit tests — warning fires/doesn't, multi-PID, self excluded, missing binary, timeout, malformed lines, grep-line filter, and a regression guard for the previously greedy pattern.

## Follow-up tightening ()
The original Linux branch used `pgrep -f "hermes.*dashboard"` — a greedy regex that matches any cmdline containing both words (e.g. a chat session discussing "dashboard" or an unrelated `grafana/dashboard-server`). Replaced with `ps -A -o pid=,command=` + the explicit patterns list already used on the Windows branch and in `hermes_cli.gateway._scan_gateway_pids`:
- `hermes dashboard`
- `hermes_cli.main dashboard`
- `hermes_cli/main.py dashboard`

## Validation
- 10/10 unit tests pass
- E2E: spawned fake `python3 -m hermes_cli.main dashboard --port 9119` via `exec -a`, confirmed detection. Also detected a real pre-existing dashboard on the same machine.

.
.