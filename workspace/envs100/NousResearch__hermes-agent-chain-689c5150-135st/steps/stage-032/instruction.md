**fix(weixin): streaming cursor, media uploads, markdown links, blank messages**

## Summary

Four fixes for the Weixin/WeChat adapter, synthesized from the best aspects of ~25 community PRs.

### 1. Streaming cursor (▉) stuck permanently
WeChat doesn't support message editing, so the cursor appended during streaming can never be removed. Adds `SUPPORTS_MESSAGE_EDITING = False` to `WeixinAdapter` and checks it in `gateway/run.py` to suppress the cursor for non-editable platforms.

**Fixes:** #8307, #8326

### 2. Media upload failures (grey boxes, 404s)
Two bugs in `_send_file()`:
- `upload_full_url` path used `PUT` → 404 on WeChat CDN. Now uses `POST`.
- `aes_key` was `base64(raw_bytes)` but the iLink API expects `base64(hex_string)` — images showed as grey boxes on the receiver side.

Also: unified both upload paths into `_upload_ciphertext()` (prefers `upload_full_url`), added `send_video`/`send_voice` methods, voice_item media builder for audio/.silk files, and `video_md5` field.

**Fixes:** #8352, #7529

### 3. Markdown links stripped
WeChat can't render `[text](url)` markdown links. `format_message()` now converts them to `text (url)` plaintext. Links inside code blocks are preserved.

**Fixes:** #7617

### 4. Blank message prevention
Three layered guards:
1. `_split_text_for_weixin_delivery('')` → `[]` not `['']`
2. `send()` filters empty/whitespace chunks before `_send_text_chunk`
3. `_send_message()` raises `ValueError` for empty text as safety net

## Files changed
- `gateway/platforms/weixin.py` — all four fixes
- `gateway/run.py` — cursor suppression for non-editable platforms
- `tests/gateway/test_weixin.py` — 15 new tests (34 total, all pass)