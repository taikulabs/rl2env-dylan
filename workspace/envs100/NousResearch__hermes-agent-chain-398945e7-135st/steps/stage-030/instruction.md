**fix(cli): recover leaked mouse tracking terminal state**

## Summary
- reset sticky terminal modes (`?1006/?1003/?1002/?1000`, focus, paste, alt-screen, Kitty keyboard, modifyOtherKeys) when the TUI starts and again on graceful signal/OOM shutdown
- expand CLI leaked-terminal sanitizer to strip SGR mouse report fragments (`ESC[<...M/m`), including visible and bare degraded forms, and recover terminal modes in-place if they are observed
- add regression coverage for escaped, visible, bare, and concatenated mouse-report leak forms plus TUI reset coverage

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_cli_terminal_response_sanitizer.py`
- `ui-tui/src/__tests__/terminalModes.test.ts`