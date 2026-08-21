**feat(cli): /timestamps command + timestamps in /history**

## Summary
`/timestamps` now toggles `[HH:MM]` message timestamps at runtime, and `/history` renders them for turns that carry a stored time.

`display.timestamps` already drove the `[HH:MM]` suffix on live submitted/streamed labels, but there was no command to flip it and `/history` ignored the setting. This wires up both.

## Changes
- `hermes_cli/commands.py`: new `/timestamps [on|off|status]` CommandDef (alias `/ts`, CLI-only).
- `cli.py`: dispatch + `/history` renders `[HH:MM]` for turns with a stored `timestamp`.
- `hermes_cli/cli_commands_mixin.py`: `_handle_timestamps_command` toggles + persists `display.timestamps`.

## Validation
| | Before | After |
|---|---|---|
| Toggle timestamps at runtime | not possible | `/timestamps on\|off\|status` |
| `/history` timestamps | never shown | `[HH:MM]` for resumed turns with a stored time |
| Live turn without stored time | n/a | no fabricated time (label unchanged) |

Invariant-safe: reuses the existing `timestamp` message key already attached by SessionDB restore and stripped before the API call (`agent/transports/chat_completions.py`, #47868) — message alternation and prompt cache untouched.

`tests/hermes_cli/test_timestamps_command.py` — 5 passing (toggle/persist, bare toggle, status no-op, `/history` shows stored-ts and omits live-turn ts, off hides all).

## Infographic

![timestamps](https://v3b.fal.media/files/b/0a9f414d/oV5hGJI0KsayTyXW_HqeW_q5USVVqB.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_timestamps_command.py`