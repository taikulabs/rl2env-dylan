**fix: rate-limit pairing rejection messages to prevent spam**

## Summary

Salvage of PR #4042 by @0xbyt4.

When `generate_code()` returns None (user rate-limited or max pending codes reached), the "Too many pairing requests" rejection message was sent on **every subsequent DM** with no cooldown. A user sending 30 messages would receive 30 identical rejection replies.

## Fix

- Check `_is_rate_limited()` **before** any pairing response — if rate limited, silently ignore
- Record rate limit after sending a rejection, so subsequent messages are silently ignored

Before: 10 messages from unauthorized user → 1 code + 9 "Too many" replies
After: 10 messages from unauthorized user → 1 code + 1 rejection + 8 silently ignored

## Follow-up

Added two tests for the new behavior:
- Rate-limited users get no response at all (silent ignore)
- Rejection messages record rate limit for subsequent suppression

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_unauthorized_dm_behavior.py`