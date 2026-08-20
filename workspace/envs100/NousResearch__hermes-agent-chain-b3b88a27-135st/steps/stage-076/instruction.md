**fix(cli): use display width for wrapped spinner height**

## What does this PR do?

Fixes a wrapped-spinner layout regression in the classic CLI/TUI footer.

A recent spinner wrap change started estimating the spinner widget height with plain `len(_spinner_text) + 16`, while the same file already uses prompt_toolkit cell-width logic for the status bar. On terminals with wide glyphs or different width semantics, that can undercount the real wrapped height and leave stale timer/status fragments behind after redraws.

This patch keeps the change minimal by making the spinner height use the exact rendered spinner string and the existing display-width helper, so the reserved height matches what prompt_toolkit actually draws.

## Related Issue

Related support thread:
https://discord.com/channels/1053877538025386074/1494814447720730855/1494814447720730855

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_cli_status_bar.py`