**fix(cron): support Telegram topic delivery via platform:chat_id:thread_id format (salvage #2037)**

## Summary
Salvage of PR #2037 by @alexferrari88, cherry-picked onto current main.

Cron job delivery to Telegram topics (forum threads) was broken — `_resolve_delivery_target()` always set `thread_id=None` when parsing the `platform:chat_id` format, so `deliver: telegram:-1003724596514:17` lost the thread ID.

### Fix
Parses the optional `:thread_id` suffix from explicit deliver targets. Handles negative Telegram chat IDs correctly via `split(':', 1)`.

- `telegram:-1003724596514:17` → chat_id=`-1003724596514`, thread_id=`17`
- `telegram:-1003724596514` → chat_id=`-1003724596514`, thread_id=`None`
- `discord:#engineering` → unchanged behavior

### Changes
- `cron/scheduler.py`: parse thread_id from deliver target
- `tests/cron/test_scheduler.py`: 2 new tests
- `tools/cronjob_tools.py`: updated schema description with thread_id format + examples

## Verification
- 5791 passed (pre-existing failures identical to main)
- Scheduler tests: 34/34 passed

## Credit
Original work by @alexferrari88 in #2037. Contributor authorship preserved via cherry-pick.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`