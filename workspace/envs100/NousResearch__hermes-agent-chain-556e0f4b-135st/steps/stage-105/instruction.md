**fix(skills): use Git Trees API to prevent silent subdirectory loss during install**

## Summary

Salvage of PR #2981 by @tugrulguner. .

When installing a skill from GitHub, `_download_directory()` made one Contents API call per subdirectory, recursing into each. If any per-directory call failed silently (rate limits, timeouts, large directories returning non-200), those subdirectory files were simply omitted — no error, no log.

## Changes

- Refactors `_download_directory()` to use the Git Trees API as the primary path (single call for the entire repo tree), falling back to the recursive Contents API when the tree endpoint is unavailable or truncated
- Added debug logging for failed subdirectory/file fetches
- 7 new tests covering tree API happy path, all fallback triggers, and recursive fallback behavior

## Follow-up fix

Simplified the tree API call by passing the branch name directly to `git/trees/{branch}?recursive=1` instead of resolving commit SHA via an extra `git/ref/heads/` call. This matches the pattern already used by `_find_skill_in_repo_tree()` from #2980.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_skills_hub.py`