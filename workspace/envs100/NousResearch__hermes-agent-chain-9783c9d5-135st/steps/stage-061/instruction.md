**fix: strip @botname suffix from Telegram slash commands (salvage #3550)**

## Summary

Telegram appends `@BotName` to slash commands in group chats (e.g. `/reset@TigerNanoBot`). `get_command()` returned `"reset@tigernanobot"` which didn't match any registered command, so commands were silently ignored in groups.

Fix: strip the `@...` suffix in `get_command()` via `split("@", 1)[0]`.

Cherry-picked from PR #3550 by @MacroAnarchy (authorship preserved). #3541 by @Kathie-yu is a duplicate of the same fix (submitted first, but without tests).