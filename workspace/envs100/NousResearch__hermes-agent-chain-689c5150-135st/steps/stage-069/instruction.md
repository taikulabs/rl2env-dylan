**fix: prevent streaming cursor (▉) from appearing as standalone Telegram messages**

## Summary

Fixes the streaming cursor (` ▉`) appearing as standalone 'white box' messages on Telegram and other platforms during rapid tool-calling.

**Reported by:** @michalkomar [on X](https://x.com/michalkomar/status/2043917218782576655)

## Problem

During rapid tool-calling, the model often emits 1-2 tokens before switching to tool calls. The stream consumer would:

1. Create a new message with `"I ▉"` (short text + cursor)
2. Model calls tools → segment break fires
3. Edit to strip cursor gets rate-limited by Telegram
4. Cursor remains as a permanent standalone message

The user saw 5 separate ▉ messages in Telegram chat — one per API call where the model briefly streamed before tool-calling.

## Fix

Added a minimum-content guard in `_send_or_edit()`: when creating a **new standalone message** (no existing message\_id), require at least 4 visible characters alongside the cursor before sending. Shorter text is skipped and accumulates into the next streaming segment.

**Unaffected paths** (all continue working normally):
- Edits to existing messages (message\_id is set → guard skipped)
- Final sends without cursor (no cursor in text → guard skipped)
- Messages with substantial text (≥4 chars → guard skipped)
- Cursor-only text (existing guard at line 635 catches this)