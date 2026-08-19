**fix(gateway): cold-start installed Windows gateway after update when none was running**

## Summary

On Windows, the post-update gateway resume path only relaunched gateways that were **running** when the update began. A gateway that had already died between updates — e.g. launched attached to a terminal/TUI that later closed, taking the child process with it — was never brought back. The Startup-folder / Scheduled-Task autostart entry only fires on the next *login*, not after an in-place update.

Concretely: a Desktop-GUI update (which invokes `hermes update --yes --gateway`) on a box whose gateway had quietly died completes with **no gateway running**, and the user gets no indication anything should have come up. This was hit in the wild — a gateway died ~9 days before a GUI update, and the update (correctly passing `--gateway`) had nothing in the "running" set to resume, so it stayed down.

## Root cause

`_pause_windows_gateways_for_update()` enumerates live gateway PIDs via `find_gateway_pids(all_profiles=True)`; if the list is empty it returns `None` and `_resume_windows_gateways_after_update()` no-ops. The resume mechanism is purely *preserve-across-update* (watch the old PID, respawn when it exits) — there is no path that *starts* a gateway that wasn't already up.

## Fix

When no gateway is running at pause time **but an autostart entry is installed** (`gateway_windows.is_installed()` — Scheduled Task or Startup-folder login item, an explicit "I want a gateway" signal), return a `cold_start_if_installed` token. The resume step then does a fresh detached spawn via `gateway_windows._spawn_detached()` — the same windowless `pythonw` + `CREATE_BREAKAWAY_FROM_JOB` path `hermes gateway start` uses. It re-checks liveness immediately before spawning so a concurrent start (the autostart entry firing) can't produce a duplicate gateway.

- **Gateway-less users get nothing forced on them** — with no autostart entry, the pause step still returns `None`.
- **POSIX unaffected** — enabled systemd units already restart via `Restart=always`; this is Windows-only.
- Best-effort throughout: logs at debug and no-ops on any error.