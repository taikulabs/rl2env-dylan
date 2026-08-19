**fix: extend ASCII-locale UnicodeEncodeError recovery to full request payload**

## Summary

Extends the existing ASCII-locale UnicodeEncodeError recovery to sanitize **all** sources of non-ASCII content in the API request — not just conversation messages.

The existing handler (from #6843) only sanitized `messages`, with a comment at line 8832 acknowledging the gap: *"Nothing to sanitize in messages — might be in system prompt or prefill. Fall through to normal error path."* This meant that on ASCII-only systems (LANG=C, Chromebooks, minimal containers), Unicode in tool descriptions, system prompts, or HTTP headers would cause unrecoverable UnicodeEncodeError.

### Changes

- **`_sanitize_structure_non_ascii()`** — generic recursive walker for nested dict/list payloads
- **`_sanitize_tools_non_ascii()`** — thin wrapper for tool schema sanitization
- **`_force_ascii_payload` flag** — once ASCII locale is detected, proactively sanitize all subsequent API calls (prevents recurring failures from new tool results bringing fresh Unicode each turn)
- **Extended error handler** now sanitizes: prefill_messages, tool schemas (`self.tools`), system prompt, ephemeral system prompt, and default HTTP headers
- Updated stale comment that acknowledged the gap

### What was dropped from #8834

Credential pool token sanitization (separate concern — silently stripping non-ASCII from tokens is a different bug from ASCII locale handling).