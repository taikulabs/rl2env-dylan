**fix(cli): non-blocking startup update check and banner deduplication**

## Summary
- cherry-pick the substantive fix from #1266 so CLI startup no longer blocks on the update check
- deduplicate the welcome banner implementation so `hermes_cli.banner.build_welcome_banner()` is the single source of truth again
- restore update-check behavior for dev/worktree installs and show update status in `hermes version`
- bring over the contributor's regression tests for update-check caching, fallback behavior, and background prefetching