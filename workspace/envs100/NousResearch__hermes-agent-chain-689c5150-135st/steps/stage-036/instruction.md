**fix(telegram): use UTF-16 code units for message length splitting**

## Summary
Port from nearai/: Telegram's 4096 message length limit is measured in UTF-16 code units, not Unicode codepoints. Astral-plane characters (emoji, CJK Extension B, musical symbols) are surrogate pairs — 1 Python char but 2 UTF-16 units. Messages heavy on emoji could silently exceed the limit.

**Changes:**
- Add `utf16_len()`, `_prefix_within_utf16_limit()`, `_custom_unit_to_cp()` helpers in base.py
- `truncate_message()` now accepts optional `len_fn` parameter
- Telegram adapter passes `len_fn=utf16_len` for splitting
- Fix fallback truncation in Telegram error handler
- `send_message_tool.py` also uses `utf16_len` for Telegram
- Comprehensive tests + mock lambda fixes for `**kw` signature change

## Tests
124 tests pass (test_platform_base.py + test_discord_reply_mode.py + test_telegram_reply_mode.py)