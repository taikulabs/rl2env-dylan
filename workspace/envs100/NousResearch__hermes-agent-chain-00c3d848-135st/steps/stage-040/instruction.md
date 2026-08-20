**fix(cli): wire approvals in background tasks**

## What does this PR do?

Fixes background CLI tasks such as `/background` and `/btw` so dangerous-command approval, sudo password, and secret capture callbacks are registered inside the background worker thread.

The foreground chat path already does this because these callbacks are stored in thread-local state. Background tasks skipped that setup, so a dangerous command in `/btw` could fall back to the raw `input()` approval prompt while prompt_toolkit owned stdin. That made the prompt effectively unanswerable and caused it to time out.

## Related Issue

Fixes #

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_cli_approval_ui.py`