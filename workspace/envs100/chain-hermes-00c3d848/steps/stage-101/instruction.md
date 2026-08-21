**fix(config): add request_timeout_seconds and stale_timeout_seconds to provider _KNOWN_KEYS**

Salvage of #16853 — cherry-picked onto current main.

## Summary
Provider-entry validator no longer warns about `request_timeout_seconds` / `stale_timeout_seconds`, which are documented in `cli-config.yaml.example` and read at runtime by `hermes_cli/timeouts.py`.

## Changes
- `hermes_cli/config.py`: add both keys to `_KNOWN_KEYS` frozenset
- `tests/hermes_cli/test_provider_config_validation.py`: positive test that the keys no longer trigger the unknown-key warning

## Validation
- Targeted: `tests/hermes_cli/test_provider_config_validation.py` — 17/17 pass
- E2E: calling `_normalize_custom_provider_entry({..., request_timeout_seconds: 300, stale_timeout_seconds: 900})` emits no warning; truly unknown keys still warn.

Credit: @vominh1919 (authorship preserved via

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_provider_config_validation.py`