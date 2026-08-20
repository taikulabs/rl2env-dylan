**fix(update): skip config migration prompts in non-interactive sessions**

## Summary

`hermes update` hangs on `input()` when run from cron jobs, scripts, or piped contexts. Now checks both `stdin.isatty()` and `stdout.isatty()`, catches `EOFError` as a fallback, and prints guidance to run `hermes config migrate` later.

Salvaged from #3446 by @phippsbot-byte with authorship preserved.

## Changes
- `hermes_cli/main.py`: guard migration prompt with dual isatty check + EOFError catch
- `tests/hermes_cli/test_cmd_update.py`: add test verifying `input()` is never called in non-interactive mode

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_cmd_update.py`