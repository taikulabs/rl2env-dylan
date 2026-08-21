**fix: platform default toolsets silently override tool deselection in hermes tools**

Salvaged from PR #2576 by @ereid7, plus read-side fix from original .

## What happened
Both the save-side and read-side fixes for this bug were originally landed in  (PR #2268). They were **inadvertently reverted** by  — a squash-merge titled "revert: remove trailing empty assistant message stripping" that bundled unrelated tools_config.py changes.

## Fixes

**Save side (`_save_platform_tools`):** Exclude platform default toolset names (`hermes-cli`, `hermes-telegram`) from preserved entries. Previously these were kept as if they were MCP server names, silently re-enabling everything the user unchecked.

**Read side (`_get_platform_tools`):** When the saved list contains explicit configurable keys (meaning the user has run `hermes tools`), use direct membership instead of subset inference. The subset approach is inherently broken when composite toolsets like `hermes-cli` resolve to ALL tools — every individual toolset appears "enabled" because its tools are a subset of the composite.

## Tests
- 10 tools_config tests pass (7 existing + 3 new regression tests from #2576)
- 598 hermes_cli tests pass

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_tools_config.py`