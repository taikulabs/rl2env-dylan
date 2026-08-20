**fix: save /plan output in workspace**

## Summary
- change `/plan` output paths from `$HERMES_HOME/plans` to workspace-relative `.hermes/plans/`
- keep the path relative on purpose so backend-aware file tools write into the active local/docker/ssh/modal/daytona workspace
- update the bundled `plan` skill, tests, and docs to describe the backend-safe behavior

## Why
`$HERMES_HOME/plans` points at the Hermes host, which is the wrong place when the active terminal backend is remote or containerized. Relative workspace paths follow the active backend cwd instead.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_skill_commands.py`
- `tests/gateway/test_plan_command.py`
- `tests/test_cli_plan_command.py`