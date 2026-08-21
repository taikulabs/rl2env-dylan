**fix(goals): make /goal work in TUI and deliver verdicts on gateway**

## Summary

`/goal` only worked in the classic CLI. In the TUI it silently did nothing. On messengers the first kickoff turn fired, but no judge verdict (`✓ Goal achieved` / `⏸ budget exhausted` / `↻ Continuing toward goal`) ever reached the user. This PR makes `/goal` work on all three surfaces.

## Root cause
- **TUI**: `/goal` was routed through the slash-worker subprocess, which set the goal row in SessionDB and then called `self._pending_input.put(state.goal)` — but the subprocess has no reader for that queue, so the kickoff was discarded. No post-turn judge hook was wired into `prompt.submit`, so even a manual kickoff would not continue the goal loop.
- **Gateway**: `_post_turn_goal_continuation` gated the verdict message on `hasattr(adapter, 'send_message')`. Adapters only expose `send()`. Dead branch on every platform.

## Changes
- `tui_gateway/server.py` — add `goal` to `_PENDING_INPUT_COMMANDS` so `slash.exec` bounces to `command.dispatch`; handle `/goal` (set / status / pause / resume / clear / stop / done) there against `GoalManager` directly; return `{type: 'send', notice, message}` on set so the TUI client renders the "Goal set" notice and fires the kickoff. Wire a post-turn judge into `_run_prompt_submit`: after `message.complete`, if a goal is active, run the judge, surface the verdict via `status.update {kind: 'goal'}`, and chain the continuation turn after the `running` guard is released so the nested call doesn't deadlock.
- `gateway/run.py` — `_post_turn_goal_continuation` now sends the verdict via `adapter.send(chat_id, content, metadata)` (with thread_id when present). Also removes the stale `self._loop` reference on the no-running-loop path.
- `ui-tui/src/gatewayTypes.ts`, `ui-tui/src/lib/rpc.ts`, `ui-tui/src/app/createSlashHandler.ts` — extend the `send` dispatch payload with an optional `notice` field. When present, the TUI prints it as a system line before firing the underlying message, so `/goal <text>` shows the confirmation AND starts the turn in one round-trip.
- `ui-tui/src/app/createGatewayEventHandler.ts` — surface `status.update {kind: 'goal'}` as a system line, matching the `compressing` convention.

## Validation
`scripts/run_tests.sh tests/tui_gateway/ tests/hermes_cli/test_goals.py tests/gateway/test_goal_verdict_send.py tests/tui_gateway/test_goal_command.py` — 102 passed (includes 16 new tests).

| Surface | Before | After |
|---|---|---|
| `/goal <text>` in TUI | silent, no visible effect | "Goal set" notice + kickoff turn runs + post-turn judge loop |
| `/goal status` / `/goal clear` etc. in TUI | silent | correct response |
| Gateway verdict messages | never delivered (dead `adapter.send_message` branch) | delivered via `adapter.send` on every platform that implements it |
| Gateway kickoff turn | worked already | unchanged |

`npm run type-check` clean.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_goal_verdict_send.py`
- `tests/tui_gateway/test_goal_command.py`