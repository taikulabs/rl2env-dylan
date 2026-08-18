**feat(tools): persistent shell mode for local and SSH backends**

## Summary

Salvage of PR #1067 by @alt-glitch, with follow-up changes:

### From PR #1067 (alt-glitch)
- New `PersistentShellMixin` in `tools/environments/persistent_shell.py` — file-based IPC protocol for long-lived bash shells
- `LocalEnvironment` and `SSHEnvironment` gain `persistent=True` option
- Output capture via temp files (stdout/stderr/exit-code), polled for completion
- Fixes latent stderr pipe buffer deadlock (`stderr=DEVNULL` on persistent shell spawn)
- New test suites: `test_local_persistent.py` (31 tests), `test_ssh_environment.py` (integration tests)

### Follow-up changes
- **SSH persistent shell enabled by default** — non-local backends benefit most from state persistence (cwd, env vars survive across commands)
- **New config option: `terminal.persistent_shell`** (default: `true`) — controls the default for non-local backends. Disable with `hermes config set terminal.persistent_shell false`
- Local backend remains opt-in via `TERMINAL_LOCAL_PERSISTENT` env var
- Precedence: per-backend env var > `TERMINAL_PERSISTENT_SHELL` > default
- Config wired through cli.py, gateway/run.py, and hermes_cli/config.py