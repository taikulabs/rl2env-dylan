**fix: report cronjob tool as available in hermes doctor**

## Summary

Sets `HERMES_INTERACTIVE=1` via `setdefault` in `run_doctor()` so CLI-gated tool checks (like cronjob management) see the same context as the interactive CLI.

### Why this works
The cronjob tool's `check_fn` requires one of `HERMES_INTERACTIVE`, `HERMES_GATEWAY_SESSION`, or `HERMES_EXEC_ASK` to report as available. Since `hermes doctor` runs from the CLI (same context as `hermes`), setting `HERMES_INTERACTIVE` is correct. Using `setdefault` ensures we don't override if already set.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_doctor.py`