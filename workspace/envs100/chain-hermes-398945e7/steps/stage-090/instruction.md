**fix(tools): reconfigure enabled unconfigured toolsets**

## What does this PR do?

Fixes the tools reconfigure menu so enabled-but-unconfigured tool categories still appear in Reconfigure. This lets users finish provider/API-key setup for tools like Web Search without disabling and re-enabling the toolset first.

## Related Issue

Discord support report: Web Search & Scraping tool reconfigure entry missing until disable/re-enable.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_tools_config.py`