**fix(providers): honor key_env/api_key_env on Azure Anthropic + accept alias in normalizer**

## Summary
Three related fixes around custom env-var-name hints for provider entries — surfaced while auditing what OpenClaw's Hermes migrator reads vs what Hermes actually honors.

## Problems

**1. Azure Anthropic path silently ignored `key_env` / `api_key_env` hints.**
If a user followed `website/docs/guides/azure-foundry.md:105` literally:
```yaml
model:
  provider: anthropic
  base_url: https://my-resource.services.ai.azure.com/anthropic
  api_key_env: MY_CUSTOM_KEY
```
Hermes raised `"No Azure Anthropic API key found. Set AZURE_ANTHROPIC_KEY or ANTHROPIC_API_KEY."` even when `MY_CUSTOM_KEY` was set in the environment. The resolver at `hermes_cli/runtime_provider.py:1126` hardcoded the two env var names and never read `model_cfg`.

**2. `_normalize_custom_provider_entry` didn't recognize `api_key_env`.**
The normalizer accepted `key_env` and the camelCase `keyEnv`, but not `api_key_env` or `apiKeyEnv`. Any user who wrote `api_key_env:` in a `custom_providers[i]` or `providers.<name>` entry got a "`unknown config keys ignored: api_key_env`" warning and the hint was dropped.

**3. `_VALID_CUSTOM_PROVIDER_FIELDS` didn't list `key_env`.**
The canonical "supported fields" set in `hermes_cli/config.py:2493` was missing `key_env`, even though the runtime reads it at `auxiliary_client.py:1889`, `runtime_provider.py:491`, `main.py:1707/2955/3293`. Documentation-as-code that drifted from reality.

## Fixes

- `hermes_cli/runtime_provider.py`: Azure Anthropic resolution now checks, in order:
  1. `os.getenv(model_cfg["key_env"])`
  2. `os.getenv(model_cfg["api_key_env"])` (docs alias)
  3. `model_cfg["api_key"]` (inline value, useful for multi-profile setups)
  4. `AZURE_ANTHROPIC_KEY` (historical default)
  5. `ANTHROPIC_API_KEY` (historical default)
  
  Error message updated to mention `key_env`/`api_key_env` as an option.

- `hermes_cli/config.py::_normalize_custom_provider_entry`: accept `api_key_env` as a snake_case alias for `key_env`, and `apiKeyEnv` as a camelCase alias. Both added to `_KNOWN_KEYS` so the "unknown config keys ignored" warning doesn't fire on valid configs.

- `hermes_cli/config.py::_VALID_CUSTOM_PROVIDER_FIELDS`: add `"key_env"`.

- `website/docs/guides/azure-foundry.md`: flip the shown field to the canonical `key_env` and add a sentence noting the accepted aliases.

## Validation

| Test suite | Before | After |
|---|---|---|
| `tests/hermes_cli/test_runtime_provider_resolution.py` | 149 passing | 161 passing (+12 new in `TestAzureAnthropicEnvVarHint` and `TestProviderEntryApiKeyEnvAlias`) |
| `tests/hermes_cli/test_azure_detect.py` | 4 passing | 4 passing |
| `tests/hermes_cli/test_config.py` | Unchanged | Unchanged |
| `tests/hermes_cli/test_provider_config_validation.py` + `test_user_providers_model_switch.py` + `test_custom_provider_model_switch.py` | 46 passing | 46 passing |

The new tests cover every path in the Azure Anthropic resolution chain (key_env hit, api_key_env alias hit, key_env-beats-fallback precedence, inline api_key, historical env var fallback, unset-var-falls-through, helpful error message, non-Azure path doesn't consult key_env) and lock the normalizer alias behavior.

## Compatibility
- Pre-existing configs using `AZURE_ANTHROPIC_KEY` / `ANTHROPIC_API_KEY` continue to work unchanged (fallback chain).
- Configs using `key_env` continue to work (already honored via normalizer, now also honored in Azure path).
- Configs using `api_key_env` (previously silently broken) now work.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_runtime_provider_resolution.py`