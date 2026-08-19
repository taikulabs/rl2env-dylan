**fix(streaming): prevent duplicate Telegram replies when stream task is cancelled**

## Summary

Fixes duplicate reply messages on Telegram when streaming is enabled. After several messages, Telegram rate-limits edit API calls, causing the stream consumer's final processing to exceed the 5-second timeout in `gateway/run.py`. The task gets cancelled, `final_response_sent` stays False, and the gateway sends the full response again via the normal path (with reply_to, appearing as a quoted reply).

**Root cause:** The `CancelledError` handler in `GatewayStreamConsumer.run()` did a best-effort final edit but never set `final_response_sent`. The gateway's `already_sent` check at line 8722+ only sets `response['already_sent']` when `final_response_sent` is True (for non-previewed responses), so the normal send path proceeded and sent a duplicate.

**Fix:** Set `final_response_sent = True` in the `CancelledError` handler when `already_sent` is True (the stream consumer had already delivered content). This is a minimal, targeted fix:
- Only 8 lines added to `stream_consumer.py`
- Zero changes to `gateway/run.py`
- Preserves all existing behavior for commentary-only sends, failed sends, and non-streaming responses