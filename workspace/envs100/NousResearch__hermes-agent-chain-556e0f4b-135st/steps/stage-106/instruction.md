**feat(model): /model command overhaul — Phases 2, 3, 5**

## Summary

Continues the `/model` command overhaul from PR #2792 (Phase 1). Implements Phases 2, 3, and 5 — Phase 4 (refactor CLI/gateway unification) is deferred to reduce regression risk.

## Phase 2: Persist base_url on model switch

**Problem:** `/model` saved `model.default` and `model.provider` but never saved `model.base_url`. After switching to a custom endpoint and restarting, the base_url was lost and resolution fell through to OpenRouter.

**Fix:**
- CLI: `save_config_value("model.base_url", ...)` when switching to a non-OpenRouter endpoint
- CLI: clears `model.base_url` (sets to `None`) when switching away from custom
- Gateway: same logic using direct YAML write (`pop("base_url")` on clear)

## Phase 3: Better feedback and edge cases

- **Bare `/model custom`** now auto-detects the model from the endpoint using `_auto_detect_local_model()` and saves all three config values atomically
- **Endpoint display** — shows the endpoint URL in success messages when switching to/from custom providers (both CLI and gateway)
- **Clear error messages** when no custom endpoint is configured
- Works in both CLI and gateway

## Phase 5: Named custom providers via `/model`

**New syntax:** `/model custom:name:model`

| Input | Result |
|-------|--------|
| `/model custom:local-server:qwen` | provider=`custom:local-server`, model=`qwen` |
| `/model custom:my-model` | provider=`custom`, model=`my-model` (unchanged) |
| `/model custom` | Switch to custom with auto-detect |

The `custom:name` provider string was already supported by `_get_named_custom_provider()` in runtime_provider.py — this just wires the parsing in `parse_model_input()`.

## Phase 4: Deferred

Unifying CLI and gateway `/model` handlers into a shared `switch_model()` function is a clean-code improvement but carries regression risk and has no user-visible benefit. Deferred to a separate PR.

## Files changed

| File | Changes |
|------|---------|
| `cli.py` | Persist base_url, bare `/model custom` handler, endpoint display |
| `gateway/run.py` | Same three changes for gateway |
| `hermes_cli/models.py` | Triple syntax parsing |
| `tests/test_cli_model_command.py` | Updated save_config_value assertion |
| `tests/hermes_cli/test_model_validation.py` | 4 new parse tests |