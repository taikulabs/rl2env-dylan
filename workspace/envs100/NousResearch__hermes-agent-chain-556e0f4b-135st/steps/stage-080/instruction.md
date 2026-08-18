**fix(terminal): log disk warning check failures at debug level (salvage #2372)**

## Summary
Salvage of PR #2372 by @aydnOktay, cherry-picked onto current main.

Two small hardening improvements to `_check_disk_usage_warning()`:

1. Moved `_get_scratch_dir()` inside the try block so exceptions from it are caught (previously could propagate uncaught)
2. Added `logger.debug(..., exc_info=True)` in the except handler for observability without changing runtime behavior
3. Added regression test verifying fail-safe behavior + debug logging on error

## Verification
- 5788 tests pass (1 new test)

## Credit
Original work by @aydnOktay in #2372. Contributor authorship preserved via cherry-pick.