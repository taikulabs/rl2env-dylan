**fix(telegram): restore DM topic typing indicator**

## What does this PR do?

Restores Telegram typing indicators for Hermes-created private DM topic lanes.

` skipped `send_chat_action()` whenever metadata had `telegram_dm_topic_reply_fallback=True`, based on the assumption that Telegram would reject `message_thread_id` for those lanes. A Discord support report from FictionBuddy says live testing shows Telegram accepts `sendChatAction` with `message_thread_id` for bot-created private DM topic lanes, and that removing the skip restores the typing indicator.

This PR removes that early return and keeps the existing non-fatal DEBUG exception handling around `send_chat_action()`, so stale/deleted threads still do not break responses.

## Related Issue

Discord support thread: "Bug Report - Telegram Typing Indicator Broken for DM Topics"

Fixes #