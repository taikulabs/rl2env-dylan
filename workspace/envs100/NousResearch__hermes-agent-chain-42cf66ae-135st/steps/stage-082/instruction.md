**fix: save /plan output in workspace**

## Summary
- change `/plan` output paths from `$HERMES_HOME/plans` to workspace-relative `.hermes/plans/`
- keep the path relative on purpose so backend-aware file tools write into the active local/docker/ssh/modal/daytona workspace
- update the bundled `plan` skill, tests, and docs to describe the backend-safe behavior

## Why
`$HERMES_HOME/plans` points at the Hermes host, which is the wrong place when the active terminal backend is remote or containerized. Relative workspace paths follow the active backend cwd instead.