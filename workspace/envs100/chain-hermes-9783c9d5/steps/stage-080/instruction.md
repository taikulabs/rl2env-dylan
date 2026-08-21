**fix(gateway): apply home channel env overrides consistently**

## Summary

Salvage of PR #1847 by @cutepawss.

Home channel env vars (`SLACK_HOME_CHANNEL`, `SIGNAL_HOME_CHANNEL`, `MATTERMOST_HOME_CHANNEL`, `MATRIX_HOME_ROOM`, `EMAIL_HOME_ADDRESS`, `SMS_HOME_CHANNEL`) were nested inside the credential-env `if` blocks in `gateway/config.py`. If a platform was already configured via `config.yaml`, setting only the home channel env var had no effect — the code never reached it.

Telegram and Discord already had the correct pattern (home channel handling outside the credential block with a `Platform.X in config.platforms` guard). This applies the same pattern to the remaining 6 platforms.

## Test
Added `TestHomeChannelEnvOverrides` covering all 6 platforms — verifies that pre-existing platform configs accept home channel env overrides.

15/15 gateway config tests pass.

. Credit to @cutepawss for finding the bug and the fix.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_send_message_missing_platforms.py`