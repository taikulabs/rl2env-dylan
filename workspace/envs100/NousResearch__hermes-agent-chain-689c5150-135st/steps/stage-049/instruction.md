**fix(agent): propagate api_mode to vision provider resolution**

## Summary

Salvage of #8871 by @luyao618 — cherry-picked onto current main.

Fixes two bugs in the vision auxiliary client path that cause crashes when the provider uses a non-default `api_mode` (e.g., `anthropic_messages` for a corporate Anthropic proxy):

1. **`api_mode` not propagated**: `resolve_vision_provider_client()` resolves `resolved_api_mode` from config but never passes it to any of its three downstream calls (`resolve_provider_client()` and `_get_cached_client()`). The non-vision path in `call_llm()` correctly passes `api_mode=resolved_api_mode` — this was a copy-paste oversight.

2. **Named custom provider stripped for vision**: `_normalize_aux_provider(for_vision=True)` returned `"custom"` instead of the named suffix, losing provider identity. `custom:corp-anthropic` became `"custom"` for vision but correctly became `"corp-anthropic"` for every other task.

3. **Dead code cleanup**: Removed the now-unused `for_vision` parameter.

## Changes
- `agent/auxiliary_client.py`: Pass `api_mode=resolved_api_mode` to all 3 downstream calls in the vision path; remove `for_vision` special case from `_normalize_aux_provider()`
- `tests/agent/test_auxiliary_named_custom_providers.py`: 2 new tests (named custom provider preservation + api_mode forwarding verification)

## Test Results
- 19/19 tests pass in `test_auxiliary_named_custom_providers.py`
- E2E verified: api_mode propagated correctly in all 3 vision code paths (explicit base_url, auto/exotic, explicit provider)