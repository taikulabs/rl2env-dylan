**fix: resolve cron auto-delivery target after dotenv reload**

## Summary
- resolve cron auto-delivery targets after reloading .env so bare-platform deliveries pick up home-channel settings before the agent run
- add a regression test covering dotenv-backed home-channel auto-delivery env injection
- clean up scheduler tests so they stop leaking un-awaited send coroutines

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cron/test_scheduler.py`