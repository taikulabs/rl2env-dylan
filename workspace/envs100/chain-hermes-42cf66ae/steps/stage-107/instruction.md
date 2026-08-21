**fix: preserve thread context for cronjob deliver=origin**

## Summary
- preserve `thread_id` in gateway session env so cron jobs created with `deliver: origin` capture the originating thread
- propagate the thread ID into cron job origin metadata
- add regression coverage for both gateway session-env propagation and cron origin capture

## What I checked first
This was not already fixed on current main.
- `GatewayRunner._set_session_env()` was setting only platform/chat/chat_name
- `_clear_session_env()` was not clearing a thread variable because none was set
- `tools/cronjob_tools._origin_from_env()` was not capturing a thread ID

That meant the scheduler's existing `origin.thread_id` support never got populated for jobs created from threaded Telegram/Slack contexts.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_session_env.py`
- `tests/tools/test_cronjob_tools.py`