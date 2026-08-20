**feat(cli): /prompt — compose your next prompt in $EDITOR**

## Summary
`/prompt` opens your editor so you can hand-write a long, multi-line prompt in markdown instead of fighting the one-line input, then sends the saved buffer as your next turn.

## Changes
- `hermes_cli/commands.py`: new `/prompt` CommandDef (alias `/compose`, CLI-only).
- `cli.py`: dispatch in `process_command`.
- `hermes_cli/cli_commands_mixin.py`: `_compose_in_editor()` (testable read-back/strip) + `_handle_prompt_compose_command()`.

## Behaviour
- `/prompt` → opens `$VISUAL`/`$EDITOR` (fallback `nano`/`notepad`) on a temp `.md` file → save & quit → buffer sent as the next agent turn.
- `/prompt <text>` pre-seeds the buffer; an empty save cancels.
- Instructional `#!` header lines are stripped.

## Validation
| | Before | After |
|---|---|---|
| Multi-line prompt authoring | one-line input only | full editor session |
| Pre-seed / cancel | n/a | `/prompt <text>` seeds; empty save cancels |

Reuses the one-shot `_pending_agent_seed` the interactive loop already consumes (same mechanism as `/blueprint`) — no changes to the input event loop or message pipeline.

`tests/hermes_cli/test_prompt_compose_command.py` — 5 passing (registration, read-back + header strip, seed set, initial-text seeding, empty-cancel), driving a fake editor subprocess.

## TUI parity
The TUI already opens `$EDITOR` via `Ctrl+G`; this adds the `/prompt` (alias `/compose`) slash command in the TUI as well, wired to the same `openEditor`. Inline text after the command seeds the composer first. Tests in `ui-tui/src/__tests__/createSlashHandler.test.ts`.

## Infographic

![prompt-editor](https://v3b.fal.media/files/b/0a9f4165/m3OKJnwg1Q0uBvUNuMNOJ_UXKp6cpL.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_prompt_compose_command.py`
- `ui-tui/src/__tests__/createSlashHandler.test.ts`