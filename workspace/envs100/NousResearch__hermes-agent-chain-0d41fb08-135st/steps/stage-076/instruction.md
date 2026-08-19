**fix(telegram): use valid reaction emojis for processing completion**

## Summary

Telegram's Bot API only allows a [specific set of emoji](https://core.telegram.org/bots/api#reactiontypeemoji) for bot reactions. `✅` (U+2705) and `❌` (U+274C) are **not** in that set, causing `on_processing_complete` reactions to silently fail with `REACTION_INVALID` (caught at debug log level by the existing try/except in `_set_reaction`).

### Changes

- **`gateway/platforms/telegram.py`**: Replace ✅/❌ with 👍/👎 in `on_processing_complete`
- **`tests/gateway/test_telegram_reactions.py`**: Update assertions + docstrings to match

The 👀 (eyes) reaction used by `on_processing_start` was already valid — no change needed.

### Credit

Based on the fix identified by @ppdng in #6685 and @r266-tech in #6097. Root cause discovered by @willy-scr in #6068.

Supersedes #6685, #6097, #5222, #2595