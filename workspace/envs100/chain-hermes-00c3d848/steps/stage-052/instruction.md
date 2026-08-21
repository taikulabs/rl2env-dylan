**fix(logging): attach gateway log after cli init**

## What does this PR do?

Fixes the `gateway.log` handler not being attached when logging is initialized in CLI mode before gateway startup.

The normal `hermes gateway run` path initializes logging early through the CLI entrypoint, then calls `setup_logging(mode="gateway")` later from `gateway/run.py`. Before this change, the second call returned immediately when `_logging_initialized` was already true, so the gateway-specific `gateway.log` handler was never attached.

This keeps logging setup idempotent, but allows a later gateway-mode call to attach the missing gateway handler. The existing rotating-handler helper already deduplicates by file path, so repeated gateway setup calls do not add duplicate handlers.

## Related Issue

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_hermes_logging.py`