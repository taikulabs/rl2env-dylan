**feat(discord): allow_any_attachment config to accept arbitrary file types**

## Summary
Discord users can now upload arbitrary file types (e.g. `.wav`, `.bin`, custom extensions) instead of only the built-in `SUPPORTED_DOCUMENT_TYPES` allowlist (PDF / text family / zip / office). Default off — historical behavior preserved.

## What was broken
Today the gateway drops any attachment whose extension isn't in the allowlist. The file gets logged as "Unsupported document type" and discarded before the agent ever sees it. A user trying to upload a `.wav` for the agent to inspect (e.g. `ffprobe` it via terminal) had no path forward.

## Changes
- `gateway/platforms/discord.py`: two new adapter helpers (`_discord_allow_any_attachment`, `_discord_max_attachment_bytes`); document branch widened to cache unknown types as `application/octet-stream` when the flag is on; `msg_type` classifier flips to `DOCUMENT` for unknown types when allowed.
- `hermes_cli/config.py`: `discord.allow_any_attachment` (default `false`) and `discord.max_attachment_bytes` (default 32 MiB; `0` = unlimited) added to `DEFAULT_CONFIG`.
- `website/docs/user-guide/messaging/discord.md`: env-var table rows + a "Receiving Arbitrary File Types" prose section.
- `website/docs/reference/environment-variables.md`: `DISCORD_ALLOW_ANY_ATTACHMENT` + `DISCORD_MAX_ATTACHMENT_BYTES` rows.
- `tests/gateway/test_discord_document_handling.py`: 9 new tests (`TestAllowAnyAttachment`) covering default-off, flag-on cache, MIME fallback to octet-stream, size cap, unlimited mode, allowlisted-doc-still-works, env fallback, config-wins-over-env, garbage-value handling.

## Behavior with the flag on
- Any uploaded file is cached under `~/.hermes/cache/documents/`.
- Surfaced to the agent as a `DOCUMENT`-typed event with `application/octet-stream` MIME — `gateway/run.py` already handles that and emits the "[The user sent a document … saved at <path>]" context note with sandbox-translated paths via `to_agent_visible_cache_path()` (Docker / Modal safe).
- File body is **not** inlined — only the path — so binary uploads don't blow up the context window.
- Allowlisted text formats (`.txt` / `.md` / `.log`) keep their existing 100 KiB inline behavior.

## Scope
Discord-only by deliberate choice. Telegram has a hard 20 MB API limit and Slack has its own caps; extending this flag to them is a separate follow-up if/when asked for.