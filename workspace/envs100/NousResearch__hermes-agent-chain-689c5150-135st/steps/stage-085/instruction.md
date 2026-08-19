**fix: detect and strip non-ASCII characters from API keys**

## Summary

Fixes the `UnicodeEncodeError: 'ascii' codec can't encode character '\u028b'` error reported by user CypherDom on macOS 13.7.

**Root cause:** The user's API key contained `ʋ` (U+028B, Latin small letter v with hook) instead of a regular `v`. This happens when copy-pasting from PDFs or web pages with decorative fonts that substitute Unicode lookalike glyphs. When httpx tries to encode the `Authorization: Bearer <key>` header as ASCII (required by HTTP spec), it fails at position 153 — exactly where the non-ASCII character sits in the key.

The existing `UnicodeEncodeError` recovery sanitized messages, tools, system prompt, and headers, but never touched the API key itself (which is injected into headers dynamically by the OpenAI SDK's `auth_headers` property).

## Changes

**Three layers of defense:**

1. **Save-time validation** (`hermes_cli/config.py`): `_check_non_ascii_credential()` strips non-ASCII from credential values when saving to `.env`, printing a clear warning with the offending characters.

2. **Load-time sanitization** (`hermes_cli/env_loader.py`): `_sanitize_loaded_credentials()` strips non-ASCII from credential env vars (those ending in `_API_KEY`, `_TOKEN`, `_SECRET`, `_KEY`) after dotenv loads, so the rest of the codebase never sees non-ASCII keys.

3. **Runtime recovery** (`run_agent.py`): The `UnicodeEncodeError` recovery block now also sanitizes `self.api_key` and `self._client_kwargs['api_key']`, closing the gap where the key persisted through message/tool sanitization.

**Bonus:** `hermes_logging.py` `RotatingFileHandler` now explicitly sets `encoding='utf-8'` instead of relying on the locale default (defensive hardening for ASCII-locale systems like macOS 13.7 with LANG=C).