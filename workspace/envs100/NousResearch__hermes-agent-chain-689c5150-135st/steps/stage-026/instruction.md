**fix: fall back to provider's default model when model config is empty**

## Summary

Fixes the `Codex Responses request 'model' must be a non-empty string` error reported by a user running OpenAI Codex OAuth.

### Root Cause

When a user configures a provider credential (`hermes auth add openai-codex`) but never selects a model via `hermes model` or `hermes setup`, the `model.default` key in `config.yaml` is empty. The gateway and CLI correctly resolve the provider (openai-codex) and credentials, but pass an empty model string to the API call, which the OpenAI Responses API rejects.

### Fix

- **`hermes_cli/models.py`**: Added `get_default_model_for_provider(provider)` — returns the first model from `_PROVIDER_MODELS` for any known provider. This is the same model shown first in the `hermes model` picker.

- **`gateway/run.py`**: In `_resolve_session_agent_runtime()`, after resolving both model and runtime, if model is empty and a provider was resolved, fill in the provider's default model. Logs an INFO message so the user knows what happened.

- **`cli.py`**: Same fallback in `_ensure_runtime_credentials()` — when model is empty after config resolution, apply the provider default before normalizing.

### Behavior

- Only triggers when model is truly empty AND a known provider was resolved
- Explicit model choices are never overridden
- Providers without a static catalog (custom, openrouter) fall through unchanged
- Logs which model was auto-selected

### Tests

12 new tests covering:
- `get_default_model_for_provider()` for known providers, unknown providers, and edge cases
- Gateway `_resolve_session_agent_runtime()` filling empty model from provider
- Gateway preserving explicitly set models
- `_resolve_gateway_model()` config reading