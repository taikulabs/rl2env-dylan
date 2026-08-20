**fix(tui): mouse + keyboard text selection in the composer**

## Summary
- Composer input now supports mouse drag selection, Shift+Arrow / Home / End extension, click-to-position, and right-click paste — selection lives inside the input, never bleeds into transcript.
- Prompt gutter (`❯ `) is a gesture region only: drags from the leading whitespace anchor input selection at offset 0 instead of starting terminal-level selection. Pre-prompt spacer row participates in the same capture.
- Click on blank composer/transcript space clears any active selection. Clearing collapses the cursor to `input.length`.
- Drop the leading prompt cell from 3 → 2 cols so the input first character lines up with the status bar `─ ready` text.
- Hide the hardware cursor while a composer selection is active so it can't auto-wrap below the prompt or paint a ghost block on the first selected cell.
- `_tui_need_npm_install` now compares the root lockfile against npm's hidden `node_modules/.package-lock.json` by content (ignoring `ideallyInert`, optional/peer-only adds) instead of by mtime, so checkouts and npm rewrites stop forcing reinstalls on every `hermes --tui`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_tui_npm_install.py`