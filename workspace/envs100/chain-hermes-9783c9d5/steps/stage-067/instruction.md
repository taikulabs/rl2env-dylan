**fix(skills): skip confirmation in /skills install and uninstall slash commands**

## Summary

Fixes the soft-lock reported in #3474 — `input()` hangs indefinitely inside prompt_toolkit's TUI event loop when running `/skills install` or `/skills uninstall` without `--yes`.

The slash command handler now unconditionally sets `skip_confirm=True`. The user typing the command is already implicit consent, and there's no safe way to call `input()` inside prompt_toolkit's event loop.

The CLI argparse path (`hermes skills install --yes`) is unaffected.

**Changes:**
- `hermes_cli/skills_hub.py` — hardcode `skip_confirm=True` in install/uninstall slash handlers, update usage strings
- `tests/hermes_cli/test_skills_skip_confirm.py` — update assertions to match new always-skip behavior

## Salvage credit

Salvaged from PR #3496 by @dlkakbs. Simplified the approach: unconditional `skip_confirm=True` instead of a `--no-confirm` flag (which had inverted semantics — it would re-enable the hanging `input()` call).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_skills_skip_confirm.py`