**feat: add system gateway service mode**

## Summary
- add an optional `hermes gateway install --system` path for Linux that installs a boot-time system service while still running the gateway as an unprivileged user
- add `--system`/`--run-as-user` gateway CLI flags plus scope-aware start/stop/restart/status/uninstall behavior
- cover the new system-service flow with gateway service tests and keep the full suite green