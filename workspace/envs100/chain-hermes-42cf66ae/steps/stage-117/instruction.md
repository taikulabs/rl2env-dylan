**fix(gateway): null-coalesce mode in SessionResetPolicy.from_dict**

## Summary

Completes YAML null handling for `SessionResetPolicy.from_dict()`. The `at_hour` and `idle_minutes` fields already had null coalescing, but `mode` was still using `data.get('mode', 'both')` which returns `None` when the key exists with an explicit null value in YAML config.

Adds a regression test covering all-null input.

Based on PR #1120 by @stablegenius49 (partially redundant — two of three fields were already fixed on main).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_config.py`