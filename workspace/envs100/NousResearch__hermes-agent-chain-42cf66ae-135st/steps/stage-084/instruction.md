**fix(discord): retry without reply reference for system messages**

## Summary
- salvage the Discord send fallback from PR #1293 onto current main
- retry the first Discord send without a reply reference when Discord rejects replying to a system message
- align the new Discord send test mock with current slash-command app_commands helpers