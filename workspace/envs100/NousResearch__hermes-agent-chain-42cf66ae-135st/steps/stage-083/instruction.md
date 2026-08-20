**fix(cli): non-blocking startup update check and banner deduplication**

## Summary
- 
- deduplicate the welcome banner implementation so `hermes_cli.banner.build_welcome_banner()` is the single source of truth again
- restore update-check behavior for dev/worktree installs and show update status in `hermes version`
- bring over the contributor's regression tests for update-check caching, fallback behavior, and background prefetching

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_check.py`