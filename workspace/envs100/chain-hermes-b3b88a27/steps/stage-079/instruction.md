**fix(gateway): slash commands never interrupt a running agent**

## Summary
Mid-run slash commands now return a friendly "busy — /stop first" message instead of silently interrupting the agent AND getting discarded.

Root cause: of 41 Discord-registered native slash commands, only 14 were in `ACTIVE_SESSION_BYPASS_COMMANDS`. The other ~15 user-facing ones (/model, /reasoning, /voice, /insights, /title, /resume, /retry, /undo, /compress, /usage, /provider, /reload-mcp, /sethome, /reset, /personality) fell through to the busy handler in `gateway/platforms/base.py`, which calls `running_agent.interrupt()` AND queues the text. After the aborted run, the safety net in `gateway/run.py` correctly identifies the queued text as a command and discards it — but the interrupt already fired. Net effect: zero-char response, dropped tool calls, user has no idea what happened.

## Changes
- `hermes_cli/commands.py`: `should_bypass_active_session()` returns True for any resolvable slash command. `ACTIVE_SESSION_BYPASS_COMMANDS` stays as the subset with dedicated Level-2 handlers.
- `gateway/run.py`: catch-all after the dedicated-handler block returns `⏳ Agent is running — `/<cmd>` can't run mid-turn. Wait for the current response or `/stop` first.` for any other recognized command.
- `gateway/platforms/discord.py`: `_run_simple_slash` logs invoker identity (user id + name + channel + guild) so future ghost-command reports can be triaged without guessing.
- `tests/gateway/test_command_bypass_active_session.py`: 15 parametrized regression cases + two assertions on `should_bypass_active_session` semantics.

## Validation
| | Before | After |
|---|---|---|
| Mid-run `/model` (Discord) | interrupt + discard, 0-char reply | `busy` message, agent keeps running |
| Mid-run `/reasoning`, `/voice`, `/insights`, `/title`, `/resume`, `/retry`, `/undo`, `/compress`, `/usage`, `/provider`, `/reload-mcp`, `/sethome`, `/reset`, `/personality` | same bug | same fix |
| Mid-run `/stop`, `/new`, `/approve`, `/deny`, `/help`, `/status`, `/agents`, `/background`, `/steer`, `/update`, `/queue`, `/restart` | worked (in bypass) | still works |
| Mid-run plain text `hello` | queued as pending | queued as pending |
| Mid-run `/foobar` (unknown) | queued as pending | queued as pending |

Targeted tests: `test_command_bypass_active_session.py` 41/41 pass, `test_steer.py` 18/18, `test_busy_session_ack.py` + `test_session_race_guard.py` 23/23.

. Related: #6252, #10370, #4665.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_command_bypass_active_session.py`