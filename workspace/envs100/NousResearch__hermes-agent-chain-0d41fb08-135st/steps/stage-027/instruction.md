**feat(gateway): add BlueBubbles iMessage platform adapter**

## Summary

Adds Apple iMessage as a first-class gateway platform via [BlueBubbles](https://bluebubbles.app/) macOS server. Consolidates the best of PRs #5869 and #4588 into a clean implementation.

### Architecture

- **Webhook-based inbound** — event-driven via local aiohttp listener (no polling, no dedup needed)
- **Email/phone → GUID resolution** — users address by `user@icloud.com` or `+155****4567`, not raw BlueBubbles GUIDs
- **Private API safety** — checks `helper_connected` before tapback/typing/read receipt calls (avoids 500s)
- **Inbound attachment downloading** — images, audio, documents fetched from BB and cached locally for agent processing
- **Markdown stripping** — clean plain-text delivery for iMessage
- **Smart progress suppression** — detects platforms without `edit_message` and silently skips tool progress (benefits any future non-editable platform too)

### Attribution

Based on PR #5869 by @benjaminsehl (webhook architecture, GUID resolution, Private API safety, progress suppression, setup wizard) with inbound attachment downloading from PR #4588 by @1960697431.

### Integration points (14 files)

| File | What |
|------|------|
| `gateway/platforms/bluebubbles.py` | Core adapter (~620 lines) |
| `gateway/config.py` | Platform enum + env config loading |
| `gateway/run.py` | Adapter factory, auth maps, progress suppression |
| `toolsets.py` | `hermes-bluebubbles` toolset + gateway composite |
| `tools/send_message_tool.py` | Platform routing + standalone send |
| `cron/scheduler.py` | Cron delivery support |
| `gateway/channel_directory.py` | Session-based discovery |
| `agent/prompt_builder.py` | iMessage platform hint |
| `hermes_cli/gateway.py` | Setup wizard entry |
| `hermes_cli/status.py` | Status display |
| `hermes_cli/tools_config.py` | Platform display config |
| `hermes_cli/config.py` | Env var registry |
| `tools/cronjob_tools.py` | Delivery description |
| `tests/gateway/test_bluebubbles.py` | 27 tests |

### Environment variables

```
BLUEBUBBLES_SERVER_URL=http://192.168.1.10:1234
BLUEBUBBLES_PASSWORD=***
BLUEBUBBLES_WEBHOOK_HOST=127.0.0.1      # default
BLUEBUBBLES_WEBHOOK_PORT=8645            # default
BLUEBUBBLES_HOME_CHANNEL=user@example.com
BLUEBUBBLES_ALLOWED_USERS=user@example.com,+155****4567
```