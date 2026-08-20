**fix(cli): handle null/non-dict display config in skin initialization**

## Summary

`display: null` or `display: "invalid"` in config.yaml crashed `init_skin_from_config` with `AttributeError`. Now falls back to default skin gracefully.

### Changes

- `hermes_cli/skin_engine.py` — `or {}` guard + isinstance check
- `tests/hermes_cli/test_skin_engine.py` — 4 test cases (None, string, int, list)

## Test Results

```
tests/hermes_cli/test_skin_engine.py  31 passed
```

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_skin_engine.py`