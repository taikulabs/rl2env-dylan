**fix(gateway): verbose tool progress no longer truncates args when tool_preview_length is 0**

## Summary

When `tool_preview_length` is 0 (the default for platforms without a tier default like Session), verbose mode was truncating args JSON to 200 characters. Since the user explicitly opted into verbose mode, they expect full tool call detail — the 200-char cap defeated the purpose.

**Before:** `_cap = _pl if _pl > 0 else 200` — always truncated to 200 chars when unset
**After:** `if _pl > 0 and len(args_str) > _pl` — no truncation when `tool_preview_length` is 0; positive values still cap

Platform message-length limits handle overflow naturally.

## Bug report

Reported by BonesGit (Session platform user) — verbose mode was still sending truncated tool call info on Session, where the platform tier defaults don't set a `tool_preview_length`.