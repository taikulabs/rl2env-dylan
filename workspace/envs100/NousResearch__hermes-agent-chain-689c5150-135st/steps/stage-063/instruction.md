**fix: auto-correct close model name matches in /model validation**

## Summary

When a user types a model name with a minor typo (e.g. `gpt5.3-codex` instead of `gpt-5.3-codex`), the `/model` command now auto-corrects to the closest match instead of accepting the wrong name with a warning that will fail at the API level.

**Before:** `/model gpt5.3-codex` → switches to `gpt5.3-codex` with a warning, but the actual API call would fail.

**After:** `/model gpt5.3-codex` → auto-corrects to `gpt-5.3-codex` with a notice.

## Changes

- **`hermes_cli/models.py`**: Added auto-correction in `validate_requested_model()` across all three validation paths (codex, custom endpoint, generic API). Uses `get_close_matches(cutoff=0.9)` — strict enough to avoid false corrections (e.g. `gpt-5.3` won't silently become `gpt-5.4`). Returns a `corrected_model` key in the validation dict.
- **`hermes_cli/model_switch.py`**: `switch_model()` now applies `corrected_model` from validation before building the result.
- **Tests**: Updated existing suggestion test, added 5 new tests for auto-correction behavior (codex typo, exact match bypass, dissimilar fallback to suggestions).

## Reported by

Discord user Nick — `/model gpt5.3-codex` on openai-codex provider.