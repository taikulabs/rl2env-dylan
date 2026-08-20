**fix: add prefix matching to slash command dispatcher**

## Summary
- salvage PR #968 onto current main by cherry-picking the contributor's commits with authorship preserved
- dispatch unique slash-command prefixes like /con to their full built-in command
- include skill slash commands in prefix resolution so runtime matching agrees with tab-completion
- guard exact-token redispatch to avoid infinite recursion on commands with extra args
- add regression coverage for unique prefixes, ambiguous prefixes, exact commands, and skill-command interactions

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_cli_prefix_matching.py`