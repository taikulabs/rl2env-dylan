**fix(telegram): escape backslashes and backticks inside code entities for Telegram (MarkdownV2)**

## Summary

- escape `\` → `\\` inside inline code and fenced code blocks per MarkdownV2 spec
- escape `` ` `` → `` \` `` inside fenced code block bodies, preserving ` ``` ` delimiters
- add 4 regression tests covering backslashes in inline code, backslashes and backticks in fenced blocks, and double-escape prevention

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_format.py`