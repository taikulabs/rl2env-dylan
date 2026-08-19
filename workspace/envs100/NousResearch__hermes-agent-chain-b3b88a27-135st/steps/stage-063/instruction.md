**fix(config): preserve ${ENV_VAR} placeholders through save_config**

## Summary
`save_config()` no longer overwrites `${ENV_VAR}` placeholders in `config.yaml` with resolved plaintext secrets. .

## Root cause
`load_config()` unconditionally calls `_expand_env_vars()`, resolving `${VAR}` to the live env value in memory. Any subsequent `save_config()` — triggered by `/model --global`, profile switches, or any other persisted change — dumped that expanded dict back to disk, silently baking the plaintext secret into `config.yaml` and destroying the user's placeholder.

## Approach
Salvaged from #11615 (binhnt92). On save, re-read the raw config from disk and walk it in parallel with the in-memory config. For each string leaf that was a `${…}` template on disk, restore the template if the in-memory value matches either:
- the env var's current expansion of that template, or
- the expansion observed at the last `load_config()` call (cached by path)

If the in-memory value has been changed to something different, it's left alone — users can still intentionally replace a templated secret with a literal, and mixed-content strings like `Bearer ${X}` are handled too.

For named list entries (e.g. `custom_providers`), matching is by `name` so reordering doesn't drop the template. Falls back to positional matching when names are duplicated.

## Why this one over the three other open PRs for #11551
| PR | Approach | Issue |
|---|---|---|
| #11579 (devorun) | Module-global reverse-map populated on expand; substring replace on save | Global state never clears, substring matching can false-positive, no tests, doesn't survive process restart |
| #11881 (kagura-agent) | Re-read raw, restore by dotted path | No safety check — blindly overwrites in-memory value with template even if user intentionally edited it |
| #10108 (allonious) | Re-read raw, restore only where current value == `os.environ[VAR]` | `re.fullmatch` means strings like `https://api.com/${PATH}` aren't handled; positional-only list matching |
| #11615 (binhnt92) — **this** | Re-read raw + cached load-time expansion + named-list matching | Semantically correct across env rotation, preserves intentional edits, handles partial templates |

Will close the other three after this merges, with credit to each contributor.

## Changes
- `hermes_cli/config.py`: add `_LAST_EXPANDED_CONFIG_BY_PATH` cache, `_preserve_env_ref_templates()`, and `_items_by_unique_name()`; `save_config()` now pipes through the preserver before serializing
- `tests/hermes_cli/test_config_env_refs.py`: 6 new scenarios covering unrelated-change, unresolved refs, intentional edits, env rotation, partial templates, duplicate-name positional fallback
- `tests/cli/test_cli_save_config_value.py`: guard for `save_config_value` path

## Validation
| | Before | After |
|---|---|---|
| `${TU_ZI_API_KEY}` survives `/model --global` | plaintext leaks to `config.yaml` | placeholder preserved |
| Targeted tests (`test_config_env_refs` + `test_config_env_expansion` + `test_cli_save_config_value`) | 19 passing | 25 passing |
| E2E: load → unrelated change → save | secret in file | placeholder in file |
| E2E: load → env var rotates → unrelated change → save | plaintext leaks | placeholder preserved, runtime uses new value |
| E2E: load → user assigns literal → save | template re-applied (bug) | literal persisted |