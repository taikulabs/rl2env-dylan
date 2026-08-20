**fix: align Nous Portal model slugs with OpenRouter naming**

## Summary

Nous Portal now passes through OpenRouter model names and routes from there. Update the static fallback model list and auxiliary client default to match.

### Changes

- **`_PROVIDER_MODELS['nous']`** in `models.py`: replaced 6 bare Nous-style names with the full OpenRouter catalog (23 models with `provider/model` format)
- **`_NOUS_MODEL`** in `auxiliary_client.py`: `gemini-3-flash` → `google/gemini-3-flash-preview`
- Updated 4 test assertions in `test_auxiliary_client.py` and `test_provider_parity.py`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_auxiliary_client.py`
- `tests/test_provider_parity.py`