**fix: prevent logging handler accumulation in gateway mode**

## Summary
- salvage the substantive fix from #902 onto current `main`
- dedupe `errors.log` `RotatingFileHandler`s by exact resolved path so gateway-created handlers are reused
- keep the current `_hermes_home` / `HERMES_HOME` behavior instead of regressing to `Path.home()`
- add regression coverage for repeated `AIAgent` initialization with an existing `errors.log` handler

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_run_agent.py`