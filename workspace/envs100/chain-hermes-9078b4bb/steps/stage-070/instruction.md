**fix(picker): keep flat-namespace reseller (opencode-go/zen) first-party models in desktop picker**

## Summary
OpenCode Go (and OpenCode Zen) now show every model they serve in the desktop and CLI model pickers — previously opencode-go rendered only 13 of 19, silently dropping `minimax-m3`, `minimax-m2.7`, `minimax-m2.5`, `glm-5`, `glm-5.1`, and `deepseek-v4-flash`.

Root cause: the picker dedup in `build_models_payload` strips any model from an aggregator row that overlaps a user-defined provider's catalog (so a local proxy isn't shadowed by OpenRouter, #45954). It gated on `is_aggregator()`, which returns True for opencode-go/zen because their flat `/v1/models` returns bare IDs the model-switch resolver searches. But those are flat-namespace **resellers**, not routing aggregators — every model they list is first-party, so deduping them against a user proxy that happens to serve a same-named model guts their own catalog.

## Changes
- `hermes_cli/providers.py`: add `is_routing_aggregator()` — True only for true routers (OpenRouter, `custom:*` proxies), False for flat-namespace resellers (opencode-go/zen). `is_aggregator()` is unchanged so model-switch flat-catalog resolution (`model_switch.py` step d) keeps working.
- `hermes_cli/inventory.py`: gate the picker dedup on `is_routing_aggregator()` instead of `is_aggregator()`.
- Tests: regression for #47077 (reseller first-party models survive overlap) + `is_routing_aggregator` unit coverage.

Both desktop picker entry points (`model.options` JSON-RPC on tui_gateway and `/api/model/options` REST on web_server) and `hermes model` all share `build_models_payload`, so every surface gets the full list.

## Validation
| | Before | After |
|---|---|---|
| opencode-go picker (user proxy overlaps) | 13 of 19 | full catalog, nothing stripped |
| OpenRouter dedup vs user proxy | strips overlap | strips overlap (unchanged) |
| `is_aggregator(opencode-go)` | True | True (unchanged) |
| `is_routing_aggregator(opencode-go)` | n/a | False |

`tests/hermes_cli/test_inventory.py` + `test_model_switch_custom_providers.py`: 60 passed. Broader model/opencode-go surface: 209 passed.

## Infographic

![windows-notifications-fixed](https://v3b.fal.media/files/b/0a9f51ae/vHq13SBSVe75r3c-Ly-6q_oFNSYvZ2.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_inventory.py`
- `tests/hermes_cli/test_model_switch_custom_providers.py`