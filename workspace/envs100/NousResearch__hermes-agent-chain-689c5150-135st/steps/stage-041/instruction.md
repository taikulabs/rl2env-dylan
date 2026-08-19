**feat(gateway): notify /restart requester when gateway comes back online**

## Summary

When a user sends `/restart` in Telegram/Discord/etc, the gateway now notifies them when it comes back online with a "♻ Gateway restarted successfully. Your session continues." message.

**Before:** After `/restart`, the user had no feedback that the gateway was back. They had to send a message to find out.

**After:** The requester gets a proactive notification in the same chat (and thread/topic) they sent `/restart` from.

## Implementation

Follows the existing `_send_update_notification` pattern (used by `/update`):

1. `_handle_restart_command` saves routing info to `.restart_notify.json` (platform, chat_id, thread_id)
2. On startup, after adapters connect, `_send_restart_notification()` reads the file, sends the message, and cleans up
3. Thread IDs are preserved via the `metadata` dict so notifications land in the correct Telegram topic or Discord thread
4. Graceful failure handling: missing adapter, send errors, missing file — all handled without crashing