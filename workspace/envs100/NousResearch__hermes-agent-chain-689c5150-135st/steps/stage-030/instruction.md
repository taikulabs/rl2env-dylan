**fix(gateway): harden Docker/container gateway pathway**

## Summary

Salvage of #8573 by @alt-glitch — cherry-picked onto current main with unrelated files removed.

Fixes the `FileNotFoundError: systemctl` crash when running gateway commands inside Docker containers.

### What changed

**Core: centralized container detection**
- Added `is_container()` to `hermes_constants.py` with process-lifetime caching (matches `is_wsl()`/`is_termux()` pattern)
- Deduped `_is_inside_container()` in `config.py` to delegate to the new function
- Replaced inline `/.dockerenv` check in `voice_mode.py`

**Gateway: defense-in-depth**
- Added `_run_systemctl()` wrapper — catches `FileNotFoundError` and raises `RuntimeError` with clear messaging. All 10 bare `subprocess.run(_systemctl_cmd(...))` call sites now route through it
- `supports_systemd_services()` now returns `False` in containers AND when `systemctl` binary is absent (`shutil.which` check)
- Docker-specific guidance in `gateway_command()` for install/uninstall/start — exit 0 instead of crashing

**CLI: accurate Docker status**
- `hermes status` shows "Manager: docker (foreground)" in containers
- `hermes dump` shows "running (docker, pid N)" or "stopped (docker)"
- `setup_gateway()` shows Docker restart policy instructions in containers

### Changes from original PR

Removed from #8573:
- `spec.md` (unrelated contributor notes)
- `Dockerfile.test` (contributor's local testing artifact)
- `uv.lock` changes (unrelated Matrix dependency additions)

All substantive code and tests preserved as-is.

### Test results

113 targeted tests pass. One pre-existing failure in `test_auth_commands.py` unrelated to these changes.