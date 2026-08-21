**fix: resolve overlay provider slug mismatch in /model picker**

## Summary

Fixes the interactive `/model` picker (Telegram/Discord) showing **0 models** for overlay providers like Copilot, Kimi, Kilocode, and others where the models.dev key differs from the Hermes provider ID.

. Salvaged from #6492 (HearthCore) and #6287 (linxule).

## Root Cause

`HERMES_OVERLAYS` keys use models.dev IDs (e.g. `"github-copilot"`) but `_PROVIDER_MODELS` curated lists and `config.yaml` use Hermes provider IDs (`"copilot"`). Section 2 of `list_authenticated_providers()` was using the overlay key directly for:

| Operation | Before | After |
|-----------|--------|-------|
| Curated model lookup | `curated.get("github-copilot")` → `[]` | `curated.get("copilot")` → 14 models |
| is_current check | `"github-copilot" == "copilot"` → False | `"copilot" == "copilot"` → True |
| Result slug | `"github-copilot"` | `"copilot"` |

**Affected providers** (overlay key ≠ Hermes slug): `github-copilot` → `copilot`, `kimi-for-coding` → `kimi-coding`, `kilo` → `kilocode`, `opencode` → `opencode-zen`, `vercel` → `ai-gateway`

## Fix

- **`model_switch.py`**: Build reverse mapping from `PROVIDER_TO_MODELS_DEV` to translate overlay keys to Hermes slugs. Also guards oauth auth store check with `if not has_creds` and checks both overlay key and Hermes slug in auth store/credential pool lookups.
- **`auth.py`**: Add `"kimi-for-coding": "kimi-coding"` alias so the picker's returned slug resolves correctly in `resolve_provider()`.

## Tests

- 5 new tests covering copilot slug resolution, no-duplicate check, kimi alias, kimi overlay resolution, kilo overlay resolution
- All 130 existing model switch tests pass
- All 10 gateway model tests pass
- E2E verified: `list_authenticated_providers(current_provider="copilot")` returns `{slug: "copilot", is_current: True, total_models: 14}`

## Files Changed

| File | Change |
|------|--------|
| `hermes_cli/model_switch.py` | Reverse-map overlay keys to Hermes slugs in Section 2 |
| `hermes_cli/auth.py` | Add kimi-for-coding alias |
| `tests/hermes_cli/test_overlay_slug_resolution.py` | New test file (5 tests) |

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_overlay_slug_resolution.py`