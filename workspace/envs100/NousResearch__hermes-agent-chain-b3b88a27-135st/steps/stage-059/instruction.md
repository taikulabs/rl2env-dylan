**fix: two process leaks (agent-browser daemons, paste.rs sleepers)**

## Summary
Two process leaks closed — agent-browser node daemons no longer accumulate when hermes sessions exit without touching the browser, and `hermes debug share` no longer spawns a 6-hour sleeping Python subprocess per paste batch. On my machine over ~3 days: 18 orphan browser daemons + 15 orphan sleep interpreters → ~2.7 GB RSS reclaimed.

## Root causes

**agent-browser:** `_reap_orphaned_browser_sessions` exists but only runs from `_start_browser_cleanup_thread`, which only fires on the first browser tool call in a process. Sessions that never touched browser → reaper never ran → orphans from crashed siblings lived forever. Cross-process orphan detection also relied on in-process `_active_sessions`, which can't see other hermes PIDs' sessions (race risk).

**paste.rs:** `_schedule_auto_delete` spawned a detached `python -c 'sleep(21600); DELETE...'` per call. No dedup, no tracking — every `hermes debug share` invocation added ~20 MB of resident Python interpreters that stuck around until the sleep finished.

## Changes

- `tools/browser_tool.py`: extract `_write_owner_pid` helper; `_run_browser_command` records owner hermes PID alongside the socket dir on every call. Reaper prefers owner_pid liveness (cross-process safe) over `_active_sessions` (kept as legacy fallback). `_emergency_cleanup_all_sessions` atexit hook now always runs the reaper — every clean hermes exit sweeps accumulated orphans.
- `hermes_cli/debug.py`: replace `subprocess.Popen` with `~/.hermes/pastes/pending.json` tracker. Added `_sweep_expired_pastes` (synchronous, best-effort, 24h grace window) called from `run_debug()` on every invocation.
- Tests: +25 cases across reaper (owner_pid alive/dead/corrupt/permission, atexit-runs-reaper, wiring test) and debug (pending.json records/merges/dedupes, sweep deletes/retains/drops-after-grace, subprocess regression guard via AST).

## Validation

|                              | Before        | After        |
|------------------------------|---------------|--------------|
| Orphan agent-browser daemons | 18 accumulated| 2 (live)     |
| paste.rs sleep interpreters  | 15 accumulated| 0            |
| RSS reclaimed                | —             | ~2.7 GB      |
| Targeted tests               | —             | 2253 pass    |

E2E with real fork()'d children: alive-owner daemon NOT reaped; dead-owner daemon SIGTERM'd and socket dir cleaned. E2E with real pending.json: entries recorded on schedule, expired entries DELETE'd on sweep, no subprocess spawned.

## Backward compatibility

- Old daemons without owner_pid files fall back to the legacy `tracked_names` check, so nothing breaks during rollout.
- Old pending subprocesses from before this PR keep sleeping as before — they'll delete their pastes and exit normally. New invocations stop creating them.