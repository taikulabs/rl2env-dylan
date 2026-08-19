**fix(cli): restore messaging toolset for gateway platforms**

## Summary
Salvage of PR #8934 by @abutbul (cherry-picked onto current main).

Adds `messaging` to `CONFIGURABLE_TOOLSETS` so that `send_message` is available on all gateway platforms (Telegram, Discord, Matrix, etc.). Without this, the toolset was silently dropped during platform tool resolution.

## What changed
- `hermes_cli/tools_config.py`: Added `("messaging", "📨 Cross-Platform Messaging", "send_message")` to `CONFIGURABLE_TOOLSETS`
- `tests/hermes_cli/test_tools_config.py`: 2 regression tests

Also addresses PRs #6140 and #6007 which fix the same issue.
, #8616.