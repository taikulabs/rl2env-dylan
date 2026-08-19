**fix(gateway): track + reap no-systemd gateway restart runtimes (WSL orphan)**

## Summary
On WSL/no-systemd hosts, a tracked gateway now survives `gateway restart` / `/restart` / dashboard / `hermes update` without leaving an orphaned, untracked listener on `:8644` — status reports it accurately, `stop` can see it, and a follow-up restart reaps the prior instance instead of stacking duplicates.

**Root cause:** With no service supervisor, `hermes gateway restart` falls to `run_gateway()` in the *same* process (`hermes_cli/gateway.py` restart branch), so the live gateway's argv stays `… gateway restart`. The strict `looks_like_gateway_command_line()` matcher only accepts `gateway run`, so process scans and the runtime-record validator both reject the live gateway → `status` says "stopped", `stop --all` can't find it, restarts can't reap the prior orphan → duplicates pile up on the port.

## Changes
- `gateway/status.py` (**@wgu9**): add `looks_like_gateway_runtime_command_line()` accepting `restart`; use it for runtime-record validation; `get_running_pid()` falls back to a validated live `gateway_state.json` PID when no pidfile path is given. Strict matcher unchanged for everything else.
- `hermes_cli/gateway.py` (**@wgu9**): `_scan_gateway_pids(include_restart_managers=…)`; `find_gateway_pids()` enables it only when `not supports_systemd_services()`, so supervised hosts never false-match a transient `gateway restart`.
- `hermes_cli/gateway.py` (follow-up): `stop_profile_gateway()` now falls back to `_reap_unsupervised_gateway_orphans()` when the pidfile/runtime record yields nothing — a profile-scoped, no-systemd-gated SIGTERM→SIGKILL of the orphan, closing the duplicate-accumulation path (suggested  in the issue). SIGKILL mirrors the field report where SIGTERM released the port but the process kept running.

## Validation
| | Before | After |
|---|---|---|
| `status` on no-systemd restart runtime | "Stopped" (alive) | accurate (running) |
| `stop` / scan sees orphan | no | yes (no-systemd only) |
| follow-up restart | stacks duplicate on `:8644` | reaps prior orphan |
| systemd host behavior | — | unchanged (gated off) |

- Targeted suite: `tests/hermes_cli/test_gateway.py tests/gateway/test_gateway_command_line_matcher.py tests/gateway/test_status.py tests/hermes_cli/test_gateway_proc_fallback.py` → **159 passed**.
- E2E (real `/proc` entry + real process, temp `HERMES_HOME`): strict matcher rejects `gateway restart`, runtime matcher accepts; `find_gateway_pids(all_profiles=True)` finds the live orphan; reaper SIGTERM/SIGKILLs it; foreign-`--profile` process is correctly **excluded** from the profile-scoped reap.

Salvage of #51468 by @wgu9 (cherry-picked, authorship preserved) + follow-up reap.

. .

## Infographic

![gateway-orphan-reaper](https://v3b.fal.media/files/b/0a9f89fb/VhRLQ_yJB-jjvhfWR15wj_kAqxgWUI.png)