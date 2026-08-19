**fix: openai-codex context length, custom provider api_mode, vision image format (#8161, #8181, #8147)**

## Summary

Three provider-related bug fixes:

### 1. Context-length lookup misses openai-codex mapping ()
`PROVIDER_TO_MODELS_DEV` was missing `"openai"` and `"openai-codex"` entries. Users on the openai-codex provider got fallback 128k context instead of the actual context window from models.dev, causing premature compression.

**Fix:** Added `"openai": "openai"` and `"openai-codex": "openai"` to the mapping dict.

### 2. api_mode not updated when switching custom providers ()
`_model_flow_named_custom()` set provider/base_url/api_key but never wrote `api_mode`. A stale api_mode from a previous provider persisted in config.yaml, causing protocol mismatches when switching between custom providers with different API modes (e.g. Anthropic-compat → OpenAI-compat).

**Fix:**
- `_named_custom_provider_map()` now extracts `api_mode` from custom_providers entries
- `_model_flow_named_custom()` applies api_mode from the entry, or pops stale api_mode to let runtime auto-detect

### 3. vision_analyze sends wrong format to Anthropic-compatible endpoints ()
`vision_tools.py` always constructed OpenAI-format `image_url` blocks, but MiniMax (`api.minimax.io/anthropic`) and similar Anthropic-compatible endpoints expect Anthropic-format `image` blocks with `source.type: base64`.

**Fix:** Added `_is_anthropic_compat_endpoint()` detection (checks provider name + URL for `/anthropic`) and `_convert_openai_images_to_anthropic()` conversion in both sync and async `call_llm()` paths. Handles base64 data URIs and URL-based images.

## Files Changed
- `agent/models_dev.py` — Added provider mappings
- `hermes_cli/main.py` — api_mode extraction and application in custom provider flow
- `agent/auxiliary_client.py` — Image block format conversion for Anthropic-compat endpoints
- `tests/agent/test_models_dev.py` — Updated test assertions
- `tests/agent/test_auxiliary_client.py` — Added image conversion tests
- `tests/hermes_cli/test_custom_provider_model_switch.py` — Added api_mode tests

## Test Results
38 targeted tests passing (all new + existing related tests).