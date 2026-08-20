**fix(cron): resolve human-friendly delivery labels via channel directory**

## Summary

Salvage of the core fix from PR #1950 by @ifrederico (which was 549 commits behind and touched 20 files).  reported by @dan-and.

### The bug

Cron jobs set `deliver: "whatsapp:Alice (dm)"` using the human-friendly labels from `send_message(action="list")`. `_resolve_delivery_target()` passed `"Alice (dm)"` as a literal `chat_id` to the WhatsApp bridge, which failed with:

```
Cannot destructure property 'user' of 'jidDecode(...)' as it is undefined.
```

### The fix

`_resolve_delivery_target()` now:
1. Strips display suffixes like `" (dm)"` or `" (group)"` from the target
2. Resolves the name via `resolve_channel_name()` from the channel directory
3. Falls back to the raw target if no match (preserves existing behavior for raw IDs)

### Tests
3 new tests covering label resolution, plain name resolution, and raw ID passthrough. 39/39 scheduler tests pass.

. . Credit to @ifrederico for the PR and @dan-and for the detailed bug report.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`