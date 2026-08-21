**feat: add gateway install scope prompts**

## Summary
- warn loudly when both user and system gateway units are installed, including guidance to remove one
- add reusable Linux setup/install helpers that let users choose user vs system gateway service during interactive setup flows
- fall back cleanly when a non-root setup session chooses a system service by printing the exact sudo follow-up command instead of bailing out

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_gateway.py`
- `tests/hermes_cli/test_gateway_service.py`