**fix: clearer docker backend preflight errors**

## Summary
- salvage the preflight Docker availability check from #940 onto current main
- preserve current `find_docker()` fallback behavior so Docker Desktop installs outside PATH still work
- add a regression test proving the preflight uses the resolved docker executable path

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_docker_environment.py`