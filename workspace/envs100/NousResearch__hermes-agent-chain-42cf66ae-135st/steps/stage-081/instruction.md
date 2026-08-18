**feat: add /plan command**

## Summary
- add a `/plan` command that loads a bundled `plan` skill instead of using a hardcoded plan prompt
- keep plans saved under `$HERMES_HOME/plans` by injecting a runtime target path alongside the skill invocation
- cover the CLI and gateway plan flow with regression tests, while keeping `/plan` visible through skill discovery/help