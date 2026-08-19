**fix: break stuck session resume loops after repeated restarts**

## Summary

 — when a session gets stuck and the user keeps restarting the gateway, the same session history reloads and traps the agent in the same stuck state. The user's only escape was manually deleting the session DB.

### The loop

1. Agent enters stuck state (hung terminal, runaway tool loop)
2. User restarts gateway
3. Session history loads with the stuck-causing context
4. User sends any message → agent gets stuck again
5. Back to step 2

### The fix

Track restart-failure counts per session in `.restart_failure_counts` (a simple JSON file). On each shutdown with active agents, increment the counter. On startup, if any session hits 3 consecutive restarts while active, auto-suspend it.

The counter resets when a session completes a turn successfully (response delivered), so planned restarts (`/restart`, `hermes update`) that happen to interrupt a session won't accumulate false counts — as long as the session works on the next attempt, the counter resets.

### How it works

| Event | Action |
|-------|--------|
| Shutdown with active agents | `_increment_restart_failure_counts()` — bumps counter for active sessions, drops inactive ones |
| Startup | `_suspend_stuck_loop_sessions()` — suspends sessions at threshold (3), clears the file |
| Successful response delivered | `_clear_restart_failure_count()` — removes session from counter file |
| Session not active during shutdown | Counter entry removed (loop was broken) |

### Design decisions

- **No SessionEntry schema changes** — pure file-based tracking
- **No database migration** — the JSON file is ephemeral and self-cleaning
- **Threshold of 3** — tolerates 1-2 restarts during normal operation (updates, config changes) without false-suspending
- **Counter drops inactive sessions** — if the session wasn't active during a restart, it wasn't stuck