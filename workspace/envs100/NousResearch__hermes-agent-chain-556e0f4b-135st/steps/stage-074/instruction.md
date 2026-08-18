**feat: @ context references + Honcho config fixes**

## Summary

### @ Context References ()
Inline `@file:path`, `@folder:dir`, `@diff`, `@staged`, `@git:N`, and `@url:` references that expand before the message reaches the LLM. Supports line ranges (`@file:main.py:10-50`), token budget enforcement (soft warn at 25%, hard block at 50%), and path sandboxing for gateway.

Core module from PR #2090 by @kshitijk4poor. CLI and gateway wiring rewritten against current main. Fixed `asyncio.run()` crash in gateway context.

### Honcho Fixes (from #1960 / #1962 by @erosika)
- Hide Honcho session banner when not explicitly configured (stray env var no longer triggers it)
- Instance-local config via `$HERMES_HOME/honcho.json` with fallback to global
- Default session strategy changed to `per-directory`

All 5685 tests pass.