**feat(config): support ${ENV_VAR} substitution in config.yaml**

## Summary

Adds `${ENV_VAR}` expansion to config.yaml values so users can reference environment variables instead of hardcoding secrets. , salvages #2680.

```yaml
auxiliary:
  vision:
    api_key: ${MY_VISION_API_KEY}
delegation:
  api_key: ${DELEGATION_KEY}
```

Unresolved references (variable not set) are kept verbatim — no silent failures. `save_config()` is untouched, so the disk file always retains the `${VAR}` template.

## Config fields this enables

The config fields where this matters most (fields that can hold secrets):
- `auxiliary.{vision,web_extract,compression,session_search,skills_hub,approval,mcp,flush_memories}.api_key`
- `delegation.api_key`
- Any custom `base_url` or other sensitive string values

Platform tokens (Telegram, Discord, etc.) already live in `.env` env vars, not config.yaml.

## What changed vs #2680

The original PR only wired expansion into `load_config()` — used by `hermes tools` and `hermes setup`. The two primary config paths were missed:

1. **`load_cli_config()` in `cli.py`** — the interactive CLI config loader (most users)
2. **Gateway module-level config in `gateway/run.py`** — bridges `api_key` values to env vars for all messaging platforms

This salvage PR adds expansion to both, plus:
- Removes redundant `import re` (already at module level)
- Adds missing PEP 8 blank lines between functions
- Adds tests for `load_cli_config()` expansion

## Implementation

- `_expand_env_vars(obj)` in `hermes_cli/config.py` — recursively walks config tree, expands `${VAR}` via `os.environ`
- Called from all three config loading paths:
  - `load_config()` (hermes tools/setup)
  - `load_cli_config()` (interactive CLI — before env var bridging)
  - Gateway module-level `_cfg` (before env var bridging)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_config_env_expansion.py`