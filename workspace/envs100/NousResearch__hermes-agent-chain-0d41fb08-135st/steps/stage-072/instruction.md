**fix(gateway): validate image downloads before caching (cross-platform)**

## Summary
Slack may return HTML sign-in/redirect pages instead of actual media bytes. This adds two layers of defense:

1. **Content-Type check** in slack.py rejects `text/html` responses early
2. **Magic-byte validation** in base.py's `cache_image_from_bytes()` rejects non-image data regardless of source platform (protects Slack, WeCom, Email, and future adapters)

Also adds ValueError guards in wecom.py and email.py so the new validation doesn't crash those adapters.

## Changes
- `gateway/platforms/base.py`: `_looks_like_image()` + validation in `cache_image_from_bytes()`
- `gateway/platforms/slack.py`: Content-Type check before caching
- `gateway/platforms/email.py`: ValueError guard
- `gateway/platforms/wecom.py`: ValueError guard (2 call sites)
- `tests/gateway/test_media_download_retry.py`: 6 new tests + existing tests updated

## Test results
30 passed

Salvaged from #6971 (@Tranquil-Flow). .