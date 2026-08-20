**fix: strip @botname suffix from Telegram slash commands (salvage #3550)**

## Summary

Telegram appends `@BotName` to slash commands in group chats (e.g. `/reset@TigerNanoBot`). `get_command()` returned `"reset@tigernanobot"` which didn't match any registered command, so commands were silently ignored in groups.

Fix: strip the `@...` suffix in `get_command()` via `split("@", 1)[0]`.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_platform_base.py`