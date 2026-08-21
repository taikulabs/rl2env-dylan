**fix(cli): prevent status bar wrapping into duplicate rows**

## Problem

The interactive CLI status bar can render as multiple visible rows over longer sessions even though it is intended to stay on a single line.

This shows up as repeated model/context rows accumulating at the bottom of the terminal when the rendered status content is just wide enough to wrap.

## Root Cause

The status bar logic was treating Python string length as a safe proxy for rendered terminal width.

That is not always true for prompt_toolkit-rendered terminal output. A fragment set that looks short enough by `len()` can still overflow the actual terminal cell width, wrap onto a second row, and leave behind duplicate-looking status lines over time.

## Fix

- measure status bar width using prompt_toolkit display cell widths instead of raw string length
- trim status bar text to the available rendered width before returning it
- add a final overflow guard in `_get_status_bar_fragments()` that collapses to a single trimmed fragment when needed
- update the status bar width test to validate rendered display width instead of `len()`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_cli_status_bar.py`