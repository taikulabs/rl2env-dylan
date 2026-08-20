**fix: preserve Anthropic cache markers through the adapter**

## Summary
- preserve assistant cache-control blocks when converting OpenAI-style messages to Anthropic format
- propagate tool-message cache markers onto generated `tool_result` blocks
- add regression tests for assistant and tool cache marker preservation

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_anthropic_adapter.py`