**fix(telegram): escape chunk indicators in MarkdownV2**

## Summary
- fix Telegram chunked MarkdownV2 messages falling back to plain text by escaping the auto-appended chunk indicator suffix
- keep the existing MarkdownV2 formatting pipeline intact instead of switching the adapter over to HTML wholesale
- add a regression test covering chunked outbound Telegram messages

## Why this approach
The reported breakage is real, but the root cause is narrow: `truncate_message()` appends a raw ` (N/M)` suffix after the message has already been converted to MarkdownV2. Telegram rejects the unescaped parentheses, then the adapter falls back to plain text.

Escaping just that suffix fixes the bug with a much smaller blast radius than rewriting the Telegram formatter around HTML mode.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_format.py`