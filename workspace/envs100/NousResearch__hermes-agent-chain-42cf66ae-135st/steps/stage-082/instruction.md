**fix(discord): retry without reply reference for system messages**

## Summary
- salvage the Discord send fallback from PR #1293 onto current main
- retry the first Discord send without a reply reference when Discord rejects replying to a system message
- align the new Discord send test mock with current slash-command app_commands helpers

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_discord_send.py`