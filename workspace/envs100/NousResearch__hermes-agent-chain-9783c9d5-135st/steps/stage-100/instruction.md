**feat(telegram): add group mention gating and regex triggers**

## Summary

Adds Discord-style mention gating for Telegram groups. Salvaged from PR #1977 by mcleay (cherry-picked with authorship preserved).

### New config options

```yaml
telegram:
  require_mention: true           # Gate group messages (default: false)
  mention_patterns:               # Regex wake-word triggers
    - "^\\s*hermes\\b"
  free_response_chats:            # Bypass gating for specific chat IDs
    - "-123456"
```

### Behavior

When `require_mention` is enabled, group messages are accepted only for:
- Slash commands
- Replies to the bot
- `@botusername` mentions
- Regex wake-word pattern matches

DMs remain unrestricted. `@mention` text is stripped before passing to the agent.

### Changes

- `gateway/platforms/telegram.py` — group gating methods + handler integration
- `gateway/config.py` — config bridges (yaml → env vars), follows Discord pattern
- `tests/gateway/test_telegram_group_gating.py` — 6 tests
- `website/docs/user-guide/messaging/telegram.md` — documentation

### Follow-up fix

Fixed `_is_group_chat` to use string comparison (`"group"`, `"supergroup"`) instead of `ChatType.GROUP` enum — the enum isn't available when python-telegram-bot isn't installed, which broke tests. Consistent with how other entity type checks work in the adapter.

### Verification

- 6/6 new group gating tests pass
- 1768 gateway tests pass, 0 failures

. Credit to mcleay for the feature.