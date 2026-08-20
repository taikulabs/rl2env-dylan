**fix(telegram): check updater/app state before disconnect**

## Summary
- 
- preserve graceful shutdown by always calling `shutdown()` once the adapter exists
- add a regression test covering disconnect with an inactive updater/app so shutdown stays quiet and completes cleanly

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_conflict.py`