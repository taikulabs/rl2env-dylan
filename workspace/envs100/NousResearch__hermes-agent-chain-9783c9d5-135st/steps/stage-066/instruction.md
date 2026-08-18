**fix(gateway): exit with failure when all platforms fail with retryable errors (salvage #3567)**

## Summary
When all messaging platforms exhaust their retry attempts and get queued for background reconnection, the gateway previously stayed alive as a zombie — no connected platforms, exit code 0, so `systemd Restart=on-failure` never triggered.

Now exits with code 1 when the last failure was retryable, letting systemd handle the restart.

Salvaged from #3567 by @kelsia14 — cherry-picked onto current main with authorship preserved. Added test updates for the new behavior.

## Changes
- `gateway/run.py`: In the `_failed_platforms` branch of `_handle_adapter_fatal_error`, exit with failure when error is retryable
- `test_platform_reconnect.py`: Updated test to expect shutdown + exit_with_failure; added new test for partial-adapter-down case
- `test_runner_fatal_adapter.py`: Updated assertion to expect shutdown with failure