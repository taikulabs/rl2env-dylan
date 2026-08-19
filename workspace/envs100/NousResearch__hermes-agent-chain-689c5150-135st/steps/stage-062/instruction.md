**feat: prompt for display name when adding custom providers**

## Summary

When adding a custom endpoint via `hermes model` → Custom endpoint, users are now prompted for a display name:

```
API base URL [e.g. https://api.example.com/v1]: http://localhost:11434/v1
API key [optional]: 
...
Context length in tokens [leave blank for auto-detect]: 
Display name [Local (localhost:11434)]: Ollama
```

The auto-generated name (e.g. `Local (localhost:11434)`) is the default — just press Enter to keep it, or type a custom label like `Ollama`, `LM Studio`, `vLLM`, etc.

This replaces the generic labels that appear in the provider menu on subsequent runs.

Prompted by user feedback from @PaulTisl.

## Changes

- **`hermes_cli/main.py`**: Extract `_auto_provider_name(base_url)` from inline logic in `_save_custom_provider()`. Add display name prompt to `_model_flow_custom()`. Add `name=` parameter to `_save_custom_provider()`.
- **`tests/cli/test_cli_provider_resolution.py`**: Update existing test for new prompt, add 4 new tests for `_auto_provider_name()` and name passthrough.