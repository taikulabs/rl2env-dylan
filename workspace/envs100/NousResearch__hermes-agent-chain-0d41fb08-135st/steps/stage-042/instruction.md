**feat(nix): shared-state permission model for interactive CLI users**

## Summary

Enables interactive CLI users in the `hermes` group to share full read-write state (sessions, memories, logs, cron) with the gateway service.

Builds on #6317 (which fixed `addToSystemPackages` to export `HERMES_HOME`) and addresses the deeper permission issues that made shared state impossible even after that fix. See also #6044 and #6145.

## Problem

Three layers prevented interactive users from writing to the managed `HERMES_HOME`:

1. **Dirs were `0750`** — group could read/traverse but not write
2. **Python forced `0700`** — `_secure_dir()` clobbered permissions on every startup (fixed by #6317's `is_managed()` guard)
3. **No mechanism for group-writable files** — even with writable dirs, files created by the gateway (umask `0022`) would be `0644`, not group-writable

## Changes

**`nix/nixosModules.nix`**
- Dirs use setgid `2770` (was `0750`) — new files inherit the `hermes` group
- `home/` stays `0750` (no interactive write needed)
- Activation script creates `HERMES_HOME` subdirs (`cron`, `sessions`, `logs`, `memories`)
- Activation migrates existing runtime files to group-writable (`chmod g+rw`); Nix-managed files (`config.yaml`, `.env`, `.managed`) stay `0640`/`0644`
- Gateway systemd unit gets `UMask=0007` so files it creates are `0660`

**`hermes_cli/config.py`**
- `ensure_hermes_home()` splits into managed/unmanaged paths
- Managed mode verifies dirs exist (raises `RuntimeError` if not) instead of `mkdir`
- Scoped `umask(0o007)` around `_ensure_default_soul_md()` so `SOUL.md` is `0660`

**`hermes_logging.py`**
- `_ManagedRotatingFileHandler` subclass applies `chmod 0660` after log rotation in managed mode
- `RotatingFileHandler.doRollover()` creates new files via `open()` which uses process umask (`0022` -> `0644`), not the scoped umask

## Usage

```nix
{
  services.hermes-agent = {
    enable = true;
    addToSystemPackages = true;
  };
  # Grant interactive user access to shared state
  users.users.myuser.extraGroups = [ "hermes" ];
}
```

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_hermes_logging.py`