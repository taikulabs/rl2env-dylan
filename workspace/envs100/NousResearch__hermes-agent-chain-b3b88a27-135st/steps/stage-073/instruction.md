**feat(execute_code): project/strict execution modes (default: project)**

## Summary
Adds a tiered execution model for `execute_code`. The new default 'project' mode runs scripts in the session's working directory with the active venv's python — so `import pandas` works, `./data.csv` resolves, and the tool generally behaves like `terminal()`. The old behavior is preserved as opt-in 'strict' mode.

## Motivation
Two recurring Discord pain points from weak models (Gemma-class especially):
1. Flip-flopping on whether `.env` / user files exist because `execute_code`'s CWD ≠ `terminal()`'s CWD
2. `ModuleNotFoundError: No module named 'pandas'` despite pandas being in the project venv that `terminal` sees fine

Root cause: `execute_code` was hardcoded to `sys.executable` + staging tmpdir. Project mode fixes both.

## What changes per mode

| | strict | **project (new default)** |
|---|---|---|
| CWD | staging tmpdir | session's `TERMINAL_CWD` (or `os.getcwd()`) |
| Python | `sys.executable` | `VIRTUAL_ENV/bin/python` → `CONDA_PREFIX/bin/python` → `sys.executable` (with Python 3.8+ version check + cache + graceful fallback) |
| Env scrubbing | ON | **ON** (identical) |
| Tool whitelist | ON | **ON** (identical) |
| Resource caps | ON | **ON** (identical) |
| Staging dir on PYTHONPATH | ✓ | ✓ (so `from hermes_tools import ...` works regardless of CWD) |

## Configuration surface
Single source of truth — `config.yaml`:

```yaml
code_execution:
  mode: project   # or 'strict'
```

No env-var override. No `.env` key. Invalid values fall back to 'project' with a log warning.

## Security posture is unchanged
The premise of this PR is that switching from strict to project changes **only** CWD and interpreter, not the security layer. Explicit regression guards enforce this:

- `test_api_keys_scrubbed_in_project_mode` — injects `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, asserts none leak into the child
- `test_secret_substrings_scrubbed_in_project_mode` — `*_SECRET`, `*_PASSWORD`, `*_CREDENTIAL`, `*_PASSWD`, `*_AUTH`
- `test_tool_whitelist_enforced_in_project_mode` — asserts `execute_code`/`delegate_task` are NOT importable from `hermes_tools` in project mode
- `test_neither_description_uses_sandbox_language` — blocks regression to ` (agents on local backends falsely believing they were sandboxed and refusing networking)

## Migration
- Schema version 18 → 19; `get_missing_config_fields()` auto-adds `code_execution.mode: project` on upgrade
- Existing users get project mode by default on first launch after upgrade

## Validation
| | Before | After |
|---|---|---|
| `tests/tools/test_code_execution.py` (existing) | 63 passed | **63 passed** |
| `tests/tools/test_code_execution_modes.py` (new, 36 tests) | — | **36 passed** |
| `tests/hermes_cli/test_config.py` (incl. version-bump fixups) | 49 passed | **49 passed** |
| `tests/test_model_tools*.py` | 38 passed | **38 passed** |
| `tests/tools/test_delegate*.py` | 72 passed | **72 passed** |

## Notes
- Remote backends (Docker/SSH/Modal/Daytona) are unchanged — they use a separate `_execute_remote` path with their own CWD semantics. Mode only affects the local backend.
- Interpreter version-check is cached via `lru_cache` so we don't fork a subprocess on every call.
- Broken venvs (missing `bin/python`, Python < 3.8, etc.) fall back cleanly to `sys.executable` rather than crashing.