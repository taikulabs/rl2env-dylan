**feat: env var passthrough for skills and user config**

## Problem

Skills can declare `required_environment_variables` in their frontmatter and Hermes stores the values securely in `~/.hermes/.env`. But the security filtering in both execution environments strips these vars before the skill's code can use them:

- **`execute_code`**: Blocks anything containing KEY, TOKEN, SECRET, PASSWORD, AUTH, CREDENTIAL in the var name (substring match)
- **`terminal` (local.py)**: Blocks vars in the `_HERMES_PROVIDER_ENV_BLOCKLIST` (explicit set built from provider/tool registries)

A skill declaring `TENOR_API_KEY` would have it stored and loaded into `os.environ`, but `execute_code` would strip it because it contains "KEY".

## Solution

Two passthrough sources, both checked before stripping:

### 1. Skill-scoped (automatic)
When a skill is loaded via `skill_view` and declares `required_environment_variables`, vars that are actually set in the environment are registered in a session-scoped passthrough set. Missing vars (still in setup_needed state) are NOT registered.

### 2. Config-based (manual)
Users can explicitly allowlist vars in config.yaml for non-skill use cases:

```yaml
terminal:
  env_passthrough:
    - MY_CUSTOM_KEY
    - ANOTHER_TOKEN
```

## Files changed

| File | Change |
|------|--------|
| `tools/env_passthrough.py` | **New** — shared passthrough registry module |
| `hermes_cli/config.py` | Add `terminal.env_passthrough` to `DEFAULT_CONFIG` |
| `tools/skills_tool.py` | Register available skill env vars on `skill_view` load |
| `tools/code_execution_tool.py` | Check passthrough before secret-substring filtering |
| `tools/environments/local.py` | Check passthrough in `_sanitize_subprocess_env` and `_make_run_env` |
| `tests/tools/test_env_passthrough.py` | 16 tests for registry + integration |
| `tests/tools/test_skill_env_passthrough.py` | 3 tests for skill loading integration |

## Security posture

- Default behavior unchanged — arbitrary LLM-generated code still can't access secrets
- Only vars explicitly declared by loaded skills OR user-configured pass through
- Skills Guard already flags suspicious env access patterns in skill content
- Missing/unset vars are not registered (can't leak what doesn't exist)