**fix: resolve cron auto-delivery target after dotenv reload**

## Summary
- resolve cron auto-delivery targets after reloading .env so bare-platform deliveries pick up home-channel settings before the agent run
- add a regression test covering dotenv-backed home-channel auto-delivery env injection
- clean up scheduler tests so they stop leaking un-awaited send coroutines