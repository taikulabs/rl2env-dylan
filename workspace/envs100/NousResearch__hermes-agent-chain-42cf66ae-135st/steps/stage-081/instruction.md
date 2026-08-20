**fix: verify crontab availability for cronjob tools**

## Summary
- 
- add regression tests covering both missing and present `crontab` binaries in interactive mode
- include the missing `shutil` import needed by the salvaged change

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_cronjob_tools.py`