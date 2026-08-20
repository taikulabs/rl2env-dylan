**fix(tools): preserve MCP toolsets when saving platform tool config**

## Summary
- preserve non-configurable platform toolset entries, including MCP server names, when hermes tools saves platform tool selections
- keep configurable toolset choices authoritative while carrying forward MCP entries already present in config.yaml
- add regression coverage for MCP preservation plus empty and malformed existing platform config

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_tools_config.py`