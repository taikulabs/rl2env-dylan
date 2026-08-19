**feat(skin): add light-mode skins + skin-aware completion menus**

## Summary

Adds two built-in light-mode skins and makes completion menu / status bar backgrounds skin-configurable. Fixes the CLI being unreadable on light terminal backgrounds.

### What changed

**From PR #9369 (chongweiliu):**
- `daylight` skin — Tailwind CSS-inspired blue/slate palette for light terminals (`#111827` near-black text, `#2563EB` blue accents)
- 6 new skin color keys: `completion_menu_bg`, `completion_menu_current_bg`, `completion_menu_meta_bg`, `completion_menu_meta_current_bg`, `status_bar_bg`, `voice_status_bg`
- Makes `_DIM` skin-aware in `cli.py` (was hardcoded `\033[2m`, now reads `banner_dim` from skin)
- Refactors `_hex_to_ansi_bold()` → `_hex_to_ansi(bold=False)` so bold is optional
- Status bar + voice status prompt_toolkit style classes
- Tests and docs

**From PR #4811 (ygd58):**
- `warm-lightmode` skin — warm brown/parchment tones for light terminals (`#2C1810` dark brown text, `#8B4513` saddle brown accents)
- Extended with completion menu + status bar color keys for full light-mode support

### How to use

```
/skin daylight        # cool blue/slate
/skin warm-lightmode  # warm brown/parchment
```

Or in `~/.hermes/config.yaml`:
```yaml
display:
  skin: daylight
```