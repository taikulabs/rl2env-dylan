**fix(cli): salvage interactive command output sanitization**

## Summary
- salvages helix4u's focused CLI ANSI/rendering fix from #11767 onto current main
- keeps the original contributor commit intact so rebase-merge preserves authorship
- routes interactive command-facing Rich output through the prompt_toolkit-safe console path when the live CLI/TUI is active

## What this fixes
Interactive slash-command output in the live CLI still had command/status paths using the raw console instead of the prompt_toolkit-safe rendering path. The user-visible bug was `/gquota` leaking mangled ANSI sequences, but the same command-path issue existed in other interactive CLI output.

This salvage keeps the original fix:
- add `HermesCLI._output_console()` / `_console_print()`
- switch command-facing `self.console.print(...)` calls in `cli.py` to the safe helper
- add focused regressions for `/gquota` and quick commands under the live TUI-style path

## Files changed
- `cli.py`
- `tests/cli/test_gquota_command.py`
- `tests/cli/test_quick_commands.py`

## Verification
Targeted PR tests:
- `scripts/run_tests.sh tests/cli/test_quick_commands.py tests/cli/test_gquota_command.py -q`
- result: `17 passed`

Broader CLI validation:
- `scripts/run_tests.sh tests/cli -q`
- result: `485 passed`

Smoke / E2E:
- `python3 -m py_compile cli.py`
- real-import smoke confirmed `_output_console()` returns the existing console when `_app` is absent and returns `ChatConsole()` when the live app is active

## Contributor credit
This PR