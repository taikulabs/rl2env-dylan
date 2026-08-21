**fix(cli): eliminate ghost status-bar + DSR input leaks from terminal drift**

## Summary
Clears the class of bugs where the CLI's status bar stacks, response text vanishes, or DSR escape responses leak into user input — all caused by prompt_toolkit's tracked `_cursor_pos.y` drifting from terminal reality.

, #5474, #8688, #14692.

## Root cause
The CLI renders through prompt_toolkit in non-full-screen mode. Every repaint uses the renderer's tracked cursor position to `cursor_up()` + `erase_down()` before redrawing. Any time that position drifts from what the terminal actually shows, new frames paint on top of stale content. Four user-visible bugs share this root cause.

## Changes
- **Idle repaints** (`cli.py:spinner_loop`) — remove the 1 Hz idle `invalidate()` tick; keep the 10 Hz tick only while a command is running. Credited to @foxion37 via 
- **Resize handler** (`cli.py:_resize_clear_ghosts`) — previously only patched column-shrink reflow. Now forces `erase_screen + cursor_goto(0,0) + renderer.reset(leave_alternate_screen=False)` on every resize so widen, row-shrink, and multiplexer-driven redraws all recover cleanly.
- **Ctrl+L / `/redraw`** (`cli.py:_force_full_redraw`, `hermes_cli/commands.py`) — new user-facing recovery path for multiplexer tab-switches that don't fire SIGWINCH (cmux, tmux). Matches bash/zsh/vim convention.
- **DSR sanitizer** (`cli.py:_strip_leaked_terminal_responses`) — strips `\x1b[<row>;<col>R` and the visible `^[[<row>;<col>R` form at the same three input sites where bracketed-paste markers are already sanitized (bracketed-paste handler, buffer text filter, process loop input).

## Validation
- `scripts/run_tests.sh tests/cli/ tests/hermes_cli/test_commands.py` → 684 passed
- New unit tests: `tests/cli/test_cli_force_redraw.py` (5 tests), `tests/cli/test_cli_terminal_response_sanitizer.py` (10 tests)
- Live PTY smoke: started `hermes chat` in isolated `HERMES_HOME`, pressed Ctrl+L while idle, injected `\x1b[53;1R/redraw` as input, exited cleanly — no traceback in `errors.log`, banner rendered, `/redraw` dispatched

| | Before | After |
|---|---|---|
| Idle status bar | duplicates ×N | stable |
| Terminal resize | ghosts on column-widen, row-shrink | clean erase every time |
| cmux/tmux tab switch | status bar stacked ×2–3 | Ctrl+L / `/redraw` recovers |
| DSR leak in input | `^[[53;1R` appears as typed text | stripped before buffer |

## Credits
- @foxion37 — PR #15428, original idle-redraw fix (commit preserved via cherry-pick, added to `AUTHOR_MAP`)
- @hennhen — #5474 reporter
- @hqulab — #12641 reporter
- @danielsotopino — #8688 reporter
- @unstoppablesssss — #14692 reporter

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_cli_force_redraw.py`
- `tests/cli/test_cli_terminal_response_sanitizer.py`