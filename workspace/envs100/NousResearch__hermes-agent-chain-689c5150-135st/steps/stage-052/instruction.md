**fix(config): restore custom providers after v11→v12 migration**

## Summary

Salvaged from PR #8814 by 墨綠BG (@BlackishGreen33), with extended coverage to all consumers.

**The bug:** The v11→v12 config migration converts `custom_providers` (a YAML list) into `providers` (a YAML dict), then deletes the original list. But all runtime resolvers still read `custom_providers`. After migration, named custom endpoints silently stop resolving — fallback chains fail with `AuthError`.

**The fix:** Adds `get_compatible_custom_providers()` in `config.py` that reads from both config schemas (legacy list + v12+ dict), normalises entries, deduplicates, and returns a unified list. All consumers now use this function.

## Changes (12 files, 496+/73-)

| File | What changed |
|------|-------------|
| `hermes_cli/config.py` | New: `_normalize_custom_provider_entry()`, `providers_dict_to_custom_providers()`, `get_compatible_custom_providers()`. Migration uses `pop()` instead of `del`. |
| `hermes_cli/runtime_provider.py` | `_get_named_custom_provider()` uses compat layer; `_resolve_named_custom_runtime()` supports `key_env`; `provider_key` matching |
| `hermes_cli/auth_commands.py` | `_get_custom_provider_names()` returns 3-tuple with `provider_key` |
| `hermes_cli/main.py` | Model picker + `_model_flow_named_custom()` handle `provider_key` + `key_env`; persist model to correct schema |
| `agent/auxiliary_client.py` | `key_env` env var support + `custom_entry.get('model')` fallback |
| `agent/credential_pool.py` | `_iter_custom_providers()` falls back to compat layer |
| `cli.py` | `/model` switch passes compat list |
| `gateway/run.py` | `/model` switch + context_length lookup use compat layer |
| `run_agent.py` | Per-model context_length lookup uses compat layer |
| `tests/hermes_cli/test_config.py` | 4 new tests: migration, runtime compat, URL key priority, dedup |
| `tests/hermes_cli/test_runtime_provider_resolution.py` | 2 new tests: providers dict resolution, key_env resolution; codex pool mock fix |
| `tests/tools/test_browser_camofox_state.py` | Fix stale version assertion (15→17) |

## Extended coverage beyond PR #8814

The original PR fixed the core runtime path but missed several consumers:
- `cli.py` + `gateway/run.py`: /model switch was still passing `cfg.get('custom_providers')`
- `run_agent.py` + `gateway/run.py`: per-model context_length lookup still read the legacy list
- `main.py` `_model_flow_named_custom()`: didn't handle `provider_key` for config persistence

All of these are now covered.