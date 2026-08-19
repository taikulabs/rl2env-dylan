**fix(tui): `/model` writes HERMES_TUI_PROVIDER unconditionally**

## Summary
`/new` after `/model <custom-provider>:<model>` now honours the user's explicit provider choice instead of silently reverting to a native provider that coincidentally has the model in its static catalog (e.g. `deepseek-v4-pro` → native `deepseek` → 401).

## Root cause
In `_apply_model_switch` (tui_gateway/server.py:850-853), `/model` set `HERMES_INFERENCE_PROVIDER` unconditionally but mirrored to `HERMES_TUI_PROVIDER` **only if it was already set**. Sessions launched without `--provider` never have `HERMES_TUI_PROVIDER` set, so on `/new`, `_resolve_startup_runtime()` skipped the explicit-provider early return (which keys off `HERMES_TUI_PROVIDER`) and fell through to `detect_static_provider_for_model()`, which matched the model name against native catalogs.

## Why fix at the `/model` writeback site, not `_resolve_startup_runtime`
@Bartok9's original PR #16873 early-returned `HERMES_INFERENCE_PROVIDER` in `_resolve_startup_runtime`. That works for this bug but partially reverts #15755 (), which deliberately removed that early return because `HERMES_INFERENCE_PROVIDER` can be ambient (shell-inherited, .env, persisted from prior processes) and ambient values shouldn't short-circuit resolution.

Brooklyn's invariant from #15755:
- `HERMES_TUI_PROVIDER` = explicit-this-process (user chose it via `--provider` or `/model`)
- `HERMES_INFERENCE_PROVIDER` = ambient (may be stale)

The real bug was that `/model` wasn't writing to the canonical "explicit" carrier. Fixing at the writeback site preserves both invariants simultaneously.

## Changes
- `tui_gateway/server.py`: `/model` now sets `HERMES_TUI_PROVIDER = target_provider` unconditionally alongside `HERMES_INFERENCE_PROVIDER`.
- `tests/test_tui_gateway_server.py`: regression test `test_config_set_model_syncs_tui_provider_unconditionally` covers the #16857 scenario (no pre-set `HERMES_TUI_PROVIDER`, custom provider selection).

## Validation
| | Before | After |
|---|---|---|
| Targeted tests (8) | N/A | all pass (`syncs_tui_provider`, `syncs_inference_provider`, `startup_runtime`) |
| E2E `/model custom:xuanji` → `/new` | resolves to native `deepseek` → 401 | resolves to `custom:xuanji` |
| E2E ambient `HERMES_INFERENCE_PROVIDER` alone | falls through to static detection | falls through to static detection (unchanged; #15755 invariant preserved) |

## Credit
Bug report, diagnosis, and initial fix: @Bartok9 in #16857 and #16873. This salvage PR reapplies the fix at the writeback site to avoid reverting #15755.

Supersedes #16873