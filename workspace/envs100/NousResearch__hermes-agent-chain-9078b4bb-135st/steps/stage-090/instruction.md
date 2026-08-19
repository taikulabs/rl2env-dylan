**feat(discord): render reasoning as -# subtext via display.reasoning_style**

## Summary
Reasoning summaries on Discord now render as `-#` subtext (native small grey metadata text) instead of a fenced code block, so thinking reads as metadata rather than chat content.

Adds a per-platform `display.reasoning_style` setting with three values:
- `code` (default everywhere except Discord) — the legacy `💭 **Reasoning:**` + fenced block
- `blockquote` — each line prefixed with `> `
- `subtext` — each line prefixed with `-# ` (Discord-only primitive)

Discord defaults to `subtext`; all other platforms keep `code`. Honours the existing `display.platforms.<platform>.reasoning_style` → `display.reasoning_style` → built-in default resolution chain.

## Changes
- `gateway/display_config.py`: new `reasoning_style` key (global default `code`, Discord platform default `subtext`) + normaliser
- `gateway/run.py`: final-message reasoning prepend resolves `reasoning_style` per-platform and renders code/blockquote/subtext
- `hermes_cli/config.py`: documents the key in `DEFAULT_CONFIG`
- `tests/gateway/test_display_config.py`: 6 tests covering defaults, overrides, normalisation

## Validation
| Style | Output |
|---|---|
| subtext (Discord) | `-# 💭 Reasoning` + `-# <line>` per line |
| blockquote | `> 💭 **Reasoning:**` + `> <line>` per line |
| code (default) | `💭 **Reasoning:**` + fenced block |

`scripts/run_tests.sh tests/gateway/test_display_config.py` → 46/46 passing. E2E-verified resolution + render with real imports against a temp HERMES_HOME.

Note: this only changes the **reasoning** render. The companion ask — ephemeral tool-progress messages — is a Discord API limitation (ephemeral requires an interaction token); `display.platforms.discord.cleanup_progress: true` is the existing answer there.

## Infographic

![reasoning-subtext-render](https://v3b.fal.media/files/b/0a9f65a7/bfxKXHvYJtHRsbRZF4oBh_zlKz6K6M.png)