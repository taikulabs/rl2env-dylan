**feat(desktop): add context usage breakdown popover**

## What does this PR do?

Adds a context usage breakdown to the Hermes Desktop status bar. Clicking the context usage indicator (e.g. `82.0k/200k`) opens a popover showing how the context window is allocated across system prompt, tool definitions, rules, skills, MCP, subagent definitions, memory, and conversation.

## Related Issue

Fixes #

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_context_breakdown.py`