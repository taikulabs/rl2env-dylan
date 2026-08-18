**feat(discord): auto-thread on @mention + skip mention in bot threads**

## Summary

Aligns Discord bot behavior with Slack: @mentions in channels auto-create threads, and follow-up messages in those threads don't require re-mentioning the bot.

## Changes

### 1. Auto-thread on @mention (default: true)

When someone @mentions the bot in a server channel, a Discord thread is automatically created from their message. The bot's response goes into the thread, giving each conversation its own isolated session — matching how Slack handles @mentions.

- Controlled by `discord.auto_thread` in config.yaml (default: `true`)
- Also readable via `DISCORD_AUTO_THREAD` env var (env takes precedence, matching existing pattern for `require_mention` and `free_response_channels`)
- The config→env bridge already existed in `gateway/config.py` (line 358)
- DMs, existing threads, and forum posts are unaffected

### 2. Skip @mention in bot-participated threads

Once the bot has responded in a thread (auto-created or manually entered), subsequent messages in that thread no longer require @mention. Users can just type normally.

- Tracked via an in-memory set (`_bot_participated_threads`) on the adapter
- Thread IDs are added when auto-creating threads and when dispatching messages in any thread
- After a gateway restart, users need to @mention once to re-establish the thread — acceptable tradeoff vs. a Discord API call per message
- Threads the bot hasn't participated in still require @mention (no change from current behavior)

### Files changed

| File | Change |
|------|--------|
| `hermes_cli/config.py` | Added `auto_thread: True` to `discord` DEFAULT_CONFIG section |
| `gateway/platforms/discord.py` | Added `_bot_participated_threads` set, changed auto-thread default from `""` to `"true"`, added `in_bot_thread` check to mention gating, added thread tracking on auto-create and dispatch |
| `tests/gateway/test_discord_free_response.py` | 7 new tests: auto-thread default, auto-thread disable, bot thread skip, unknown thread still requires mention, auto-thread tracks participation, dispatch tracks participation |
| `tests/gateway/test_discord_slash_commands.py` | Updated `test_auto_thread_disabled_by_default` → `test_auto_thread_enabled_by_default_slash_commands` + added `test_auto_thread_can_be_disabled` |

### Test results

All 903 gateway tests pass (0 failures). Full suite: 4421 passed.