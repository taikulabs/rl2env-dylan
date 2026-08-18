**fix: add download retry to cache_audio_from_url matching cache_image_from_url**

PR #3323 added retry with exponential backoff to `cache_image_from_url` but missed the sibling function `cache_audio_from_url` — 18 lines below in the same file, same single-shot download pattern. A single transient 429, 5xx, or timeout now loses voice messages from Discord, Telegram, and WhatsApp, while image downloads survive them.

## Changes Made

Applied the identical retry pattern from `cache_image_from_url` to `cache_audio_from_url` in `gateway/platforms/base.py`:
- 3 attempts (initial + 2 retries) with 1.5s exponential backoff
- Retries on `httpx.TimeoutException` and `httpx.HTTPStatusError` >= 429
- Immediate raise on non-retryable 4xx (e.g. 404)
- Debug logging on each retry attempt