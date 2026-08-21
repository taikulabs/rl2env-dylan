**fix(cli): handle EOFError in sessions delete/prune confirmation prompts**

`hermes sessions delete` and `hermes sessions prune` crash with `EOFError` when stdin is not a TTY (piped input, CI/CD, cron scripts).

Extracts a `_confirm_prompt()` helper that catches `EOFError` and `KeyboardInterrupt`, defaulting to cancel. Both call sites use it instead of duplicated try/except blocks.

Includes 2 new tests verifying both commands cancel gracefully on EOF.

Salvaged from PR #2622 by @dieutx (improved from duplicated try/except to shared helper). .

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_sessions_delete.py`