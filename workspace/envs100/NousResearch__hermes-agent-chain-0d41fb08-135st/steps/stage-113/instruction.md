**fix(custom-providers): propagate model field from config so API receives the correct model name**

## Summary

Salvage of PR #7916 by @0xFrank-eth. .

When a `custom_providers` entry in `config.yaml` defines a `model` field that differs from the entry's `name`, the model string was silently dropped during runtime resolution. The API received the provider name (e.g., "my-dashscope") instead of the actual model name (e.g., "qwen3.6-plus"), causing 400 errors.

## Changes

### Cherry-picked from PR #7916 (contributor: @0xFrank-eth):
- `_get_named_custom_provider()` now reads the `model` field from config entries
- `_resolve_named_custom_runtime()` propagates model into its return dict
- `cli.py` `_ensure_runtime_credentials()` overrides `self.model` when runtime carries a model

### Follow-up fixes:
- **Critical:** The original fix placed model propagation *after* the credential pool early-return in `_resolve_named_custom_runtime()`, making it dead code when a pool is active (which happens whenever `custom_providers` has an `api_key` that auto-seeds the pool). Fixed by injecting model into `pool_result` before returning.
- Added `model` to `_VALID_CUSTOM_PROVIDER_FIELDS` in config validation
- Added 5 regression tests covering: model extraction from config, empty/whitespace model exclusion, direct resolution path, credential pool path, and absent model field