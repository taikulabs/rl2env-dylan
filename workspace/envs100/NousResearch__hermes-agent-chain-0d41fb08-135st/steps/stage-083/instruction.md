**fix: per-profile subprocess HOME isolation**

## Summary

Isolates system tool configs (git, ssh, gh, npm) per profile by injecting a per-profile HOME into **subprocess environments only**. The Python process's own `os.environ["HOME"]` and `Path.home()` are never modified.

## The problem

Two related bugs share a root cause:
1. **Docker**: tool configs written to `/root/` don't persist when the container is recreated — only `/opt/data` (the persistent volume) survives.
2. **Profiles**: all profiles share `/root/`'s git identity, SSH keys, gh tokens, etc.

## Why previous approaches were rejected

PR #4437 and PR #4685 both set `os.environ["HOME"]` globally in the Python process. This breaks `Path.home()` which is used by 42 files — profile infrastructure (`_get_profiles_root()`, `_get_default_hermes_home()`, `_get_wrapper_dir()`), systemd/launchd paths, and every Python library that calls `os.path.expanduser()`.

## This approach: subprocess-only injection

Every subprocess the agent spawns goes through one of three choke points that already build custom env dicts. We inject `HOME={HERMES_HOME}/home/` at these three points:

| Choke point | File | Covers |
|-------------|------|--------|
| `_make_run_env()` | `tools/environments/local.py` | Foreground terminal commands |
| `_sanitize_subprocess_env()` | `tools/environments/local.py` | Background processes (PTY + non-PTY) |
| `child_env` construction | `tools/code_execution_tool.py` | execute_code sandbox |

Single source of truth: `hermes_constants.get_subprocess_home()`

## Activation

Directory-based — zero config needed:
- **`{HERMES_HOME}/home/` exists** → subprocesses get it as HOME
- **Doesn't exist** → behavior unchanged

Who creates the directory:
- **Docker**: `entrypoint.sh` bootstraps it inside the persistent volume
- **Named profiles**: added `"home"` to `_PROFILE_DIRS` in profiles.py
- **Default non-Docker installs**: not created → zero behavior change

## What this preserves

- `Path.home()` untouched → profile infrastructure, systemd paths, wrapper dirs all work
- `os.environ["HOME"]` untouched → no impact on Python process internals
- Shell initialization unaffected — `bash -c` (non-login, used for terminal commands) doesn't source profile files

## Changes

| File | Change |
|------|--------|
| `hermes_constants.py` | New `get_subprocess_home()` — returns `{HERMES_HOME}/home/` if it exists |
| `tools/environments/local.py` | Inject HOME in `_make_run_env()` and `_sanitize_subprocess_env()` |
| `tools/code_execution_tool.py` | Inject HOME in child_env construction |
| `hermes_cli/profiles.py` | Add `"home"` to `_PROFILE_DIRS` |
| `docker/entrypoint.sh` | Add `home` to bootstrapped directories |
| `tests/test_subprocess_home_isolation.py` | 13 tests covering all paths |