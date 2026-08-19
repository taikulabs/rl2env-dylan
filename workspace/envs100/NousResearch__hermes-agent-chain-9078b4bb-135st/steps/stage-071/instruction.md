**feat(goals): /goal wait <pid> — park the loop on a background process**

## Summary
Adds `/goal wait <pid>` — a wait barrier that **parks** the standing-goal loop on a background process instead of re-poking the agent every turn while it waits.

The `/goal` loop runs a post-turn judge after every turn and re-fires a continuation prompt until the goal is done. When a goal is gated on a long-running background process that hasn't produced anything to judge yet — CI on a pushed PR, a build, a test matrix, a deploy — this spins the agent into "is it done yet?" busy-work and burns the turn budget for nothing. There was previously no way to say "park until this finishes."

## How it works
- `/goal wait <pid> [reason]` records a barrier on the active goal. While that PID is alive, `evaluate_after_turn` short-circuits: **no judge call, no turn consumed, no continuation prompt**. `/goal status` shows `⏳ Goal (parked on <reason>): <goal>`.
- The barrier **auto-clears the moment the process exits** (lazy liveness check), so the next turn resumes normal judging — pair it with a `terminal(background=true, notify_on_complete=true)` watcher whose completion notification wakes the session.
- `/goal unwait` clears it manually; `pause` / `resume` / `clear` all drop it; a dead or stale PID can never wedge the loop (resolves to "not waiting").

## Changes
- `hermes_cli/goals.py`: `GoalState` gains backward-compatible `waiting_on_pid` / `waiting_reason` / `waiting_since`; new `wait_on()` / `stop_waiting()` / `is_waiting()` manager methods; cross-platform `_pid_alive()` (psutil → POSIX fallback); barrier short-circuit in `evaluate_after_turn`; parked indicator in `status_line`; barrier dropped on pause/resume.
- `hermes_cli/cli_commands_mixin.py` + `gateway/slash_commands.py`: `/goal wait` / `/goal unwait` subcommands (CLI + gateway parity).
- `gateway/run.py`: mid-run command guard allows `wait` / `unwait` (control-plane only, safe while the agent is running).
- `hermes_cli/commands.py`: updated `/goal` args hint.
- Docs: new "Parking on a background process" section in `goals.md`.

## Validation
| Check | Result |
|---|---|
| New barrier unit tests (live PID parks, exit auto-resumes, dead PID never parks, persist/reload, pause/resume clear, backward-compat load) | 12 added |
| `tests/hermes_cli/test_goals.py` | 64 pass |
| goal-command surface (CLI interrupt, tui_gateway, gateway notice/max-turns, command registry) | 171 pass |
| Backward compatibility | old `state_meta` rows load with no barrier |

## Infographic
![/goal wait — park the loop on a background process](https://v3b.fal.media/files/b/0a9f4140/KQgGN5bKRBmvsRZNydUOu_DoLWrSWs.png)