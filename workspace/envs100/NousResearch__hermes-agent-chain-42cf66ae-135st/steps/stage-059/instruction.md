**fix: resolve delegation providers from custom_providers**

## Summary
- salvage PR #1012 onto current main by cherry-picking the contributor's runtime-provider fix with authorship preserved
- resolve delegation providers from config.yaml custom_providers when delegation uses either the raw saved name (for example local) or the menu-key form (custom:local)
- keep raw custom names from shadowing built-in provider ids like nous
- keep the regression coverage aligned with current main while retaining tests for saved credentials, env fallback, and builtin-vs-custom precedence

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_runtime_provider_resolution.py`