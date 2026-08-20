**docs: add provider contribution guide**

## Summary
- add a dedicated developer guide page for adding first-class inference providers
- document the two implementation paths: OpenAI-compatible vs native provider adapters
- link the new page from provider runtime, architecture, contributing, and the docs sidebar

## Validation
- npm install (website)
- npm run build

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_prompt_builder.py`
- `tests/cron/test_scheduler.py`
- `tests/tools/test_send_message_tool.py`