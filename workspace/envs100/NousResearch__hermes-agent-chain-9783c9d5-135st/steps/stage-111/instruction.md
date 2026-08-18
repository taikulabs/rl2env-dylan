**fix(honcho): write config to instance-local path for profile isolation**

## Summary

Fixes the bug where multiple agents/profiles running `hermes honcho setup` all write to the shared global `~/.honcho/config.json`, overwriting each other's configuration.

Reported by stridell on Discord.

## Root Cause

`_write_config()` in `honcho_integration/cli.py` defaulted to `resolve_config_path()` which returns the global `~/.honcho/config.json` when no instance-local file exists yet — i.e. on every first setup. All profiles' first setup writes hit the same file.

## Fix

- Added `_local_config_path()` which always returns `$HERMES_HOME/honcho.json`
- Changed `_write_config()` to default to `_local_config_path()` instead of `_config_path()`
- **Reading** still falls back to global via `resolve_config_path()` for cross-app interop and seeding initial values
- Updated `cmd_setup` and `cmd_status` messaging to show the correct write path

## Behavior After Fix

| Operation | Path Used |
|-----------|-----------|
| Read (no local file) | `~/.honcho/config.json` (global fallback) |
| Read (local file exists) | `$HERMES_HOME/honcho.json` |
| Write (all commands) | `$HERMES_HOME/honcho.json` (always) |

First setup: reads from global (seeds values), writes to local. Subsequent operations: reads and writes the local file. Each profile is fully isolated.

## Tests

10 new tests in `tests/honcho_integration/test_config_isolation.py`:
- `_local_config_path` always returns instance-local path
- Write creates local file, doesn't touch global
- Read falls back to global when no local file exists
- Local takes priority over global on read
- Two profiles get fully separate configs
- First setup seeds from global, writes to local