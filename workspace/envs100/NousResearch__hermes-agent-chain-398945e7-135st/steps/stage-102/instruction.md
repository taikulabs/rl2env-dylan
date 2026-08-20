**fix(file): strip leaked terminal fences from reads**

Salvage of #19266 by @LeonSGP43 onto current main.

## Summary
Strip leaked `__HERMES_FENCE_` markers, BEL characters, and OSC-title fragments from `ShellFileOperations` read outputs. These leak into paginated reads, raw reads, and metadata/sample command outputs on shells that echo the fence bracketing. .

## Changes
- tools/shell_file_operations.py (and friends): cleanup applied across paginated / raw / sample paths (+89/-7)
- tests: regressions for paginated and raw reads with leaked fence wrappers

## Validation
scripts/run_tests.sh tests/tools/test_file_operations.py → 52 passed

Original PR: #19266

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_file_operations.py`