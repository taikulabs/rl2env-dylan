**feat: add /plan command**

## Summary
- add a `/plan` command that loads a bundled `plan` skill instead of using a hardcoded plan prompt
- keep plans saved under `$HERMES_HOME/plans` by injecting a runtime target path alongside the skill invocation
- cover the CLI and gateway plan flow with regression tests, while keeping `/plan` visible through skill discovery/help

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_skill_commands.py`
- `tests/gateway/test_plan_command.py`
- `tests/test_cli_plan_command.py`