**fix: improve WhatsApp UX — chunking, formatting, streaming**

## Summary

Addresses user complaints about poor WhatsApp experience ([tweet from @joaopanizzutti](https://x.com/joaopanizzutti)): "sends the whole code all the time" and "terminal gets interrupted and gets cooked."

Competitive analysis of OpenClaw's WhatsApp implementation revealed three root causes in our adapter, all fixed here.

## Changes

### 1. Reclassify WhatsApp from TIER_LOW → TIER_MEDIUM (`display_config.py`)
The Baileys bridge already implements a `/edit` endpoint, so WhatsApp supports message editing — it was incorrectly grouped with platforms that don't (Signal, WeChat). This single-line change enables:
- **Streaming**: progressive response delivery instead of buffering the entire response
- **Tool progress**: "new" mode shows users what tools are running (vs silence)

### 2. Fix `send()` — add chunking + formatting (`whatsapp.py`)
- **MAX_MESSAGE_LENGTH**: 65536 → 4096 (practical UX limit — 64K messages are unreadable on mobile)
- **send()** now calls `format_message()` and `truncate_message()` before sending, then loops through chunks with 300ms delay between them
- `reply_to` only set on the first chunk
- Empty/whitespace-only messages return early (matches Telegram pattern)
- The base class `truncate_message()` already handles code block boundary detection (closes/reopens ``` fences at chunk boundaries)

### 3. Override `format_message()` — markdown → WhatsApp conversion (`whatsapp.py`)
WhatsApp uses different formatting syntax than standard markdown:
- `**bold**` → `*bold*`
- `__underline__` → `*bold*` (WhatsApp has no underline)
- `~~strike~~` → `~strike~`
- `# headers` → `*headers*` (bold text)
- `[text](url)` → `text (url)`
- Code blocks and inline code are **protected** from conversion via placeholder substitution (same approach as OpenClaw's `markdownToWhatsApp()`)

## What this fixes
- **"sends the whole code all the time"** → messages chunked at 4K with proper WhatsApp formatting and code block preservation
- **"terminal gets interrupted and gets cooked"** → streaming + tool progress give visual feedback so users don't send follow-up messages that interrupt the running agent

## Future improvements (not in this PR)
- Per-platform `busy_input_mode` default (currently global config only)
- WhatsApp-specific code block handling (send as document attachment for very long blocks)