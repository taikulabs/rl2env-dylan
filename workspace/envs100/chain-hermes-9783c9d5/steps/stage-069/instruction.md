**fix: add self-termination guard for pkill/killall targeting hermes/gateway**

## Summary

Prevent the agent from accidentally killing its own process with `pkill -f gateway`, `killall hermes`, `pkill -f "cli.py --gateway"`, etc. Adds a dangerous command pattern to `DANGEROUS_PATTERNS` that triggers the approval flow before execution.

Salvaged from #3400 by @arasovic with authorship preserved. #3402 is a duplicate (3 lines, no tests) — should be closed.

## Changes
- `tools/approval.py`: add self-termination regex pattern
- `tests/tools/test_approval.py`: 4 tests (pkill hermes, killall hermes, pkill gateway, pkill unrelated not flagged)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_approval.py`