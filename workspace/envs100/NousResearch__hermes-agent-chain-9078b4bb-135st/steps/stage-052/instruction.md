**feat(cli): Ctrl+G submits the edited draft on save (TUI parity)**

## Summary
Ctrl+G now submits your edited prompt when you save and close `$EDITOR`, instead of just loading the text back into the input area.

Ctrl+G already opened the current draft in `$EDITOR`, but used `open_in_editor(validate_and_handle=False)` — the saved text returned to the input and you still had to press Enter. The TUI's Ctrl+G (`openEditor`) submits on clean exit; this brings the classic CLI to parity.

## Why not just `validate_and_handle=True`
CLI submission is driven by the custom `enter` keybinding, not the buffer's `accept_handler`, so prompt_toolkit's `validate_and_handle` doesn't route through it. Instead a done-callback on the editor Task calls the new `_submit_editor_buffer()`, which mirrors the Enter handler's branches.

## Changes
- `cli.py`: `_open_external_editor` chains a Task done-callback; new `_submit_editor_buffer()` + `_reset_input_buffer()` helpers.

## Behaviour
| Save state | Result |
|---|---|
| non-empty, idle | submitted as next prompt |
| non-empty, agent busy | queued / interrupt per `/busy` mode |
| `/slash...` | dispatched via `process_command` |
| empty save / editor cancel | nothing submitted |

`tests/hermes_cli/test_ctrlg_editor_submit.py` — 5 passing (idle send, empty no-op, busy queue, busy interrupt, slash dispatch).

## Infographic

![ctrlg-submits](https://v3b.fal.media/files/b/0a9f4464/r8UjM_E54jWO5L6bsYCwC_mTVD0grb.png)