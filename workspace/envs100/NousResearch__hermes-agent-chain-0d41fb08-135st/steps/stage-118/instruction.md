**fix: normalize checkpoint manager home-relative paths**

## Summary

Salvage of #7898 by @faishal882 ().

`Path.resolve()` does not expand `~` — only `Path.expanduser()` does. The checkpoint manager had 11 instances of bare `.resolve()` that broke when paths contained `~` (e.g. `~/.hermes`, `~/.config`), producing invalid paths like `/root/~/.hermes`.

### Changes

- Adds `_normalize_path()` helper: `Path(x).expanduser().resolve()`
- Replaces all 11 bare `.resolve()` calls (including `_validate_file_path` which was added after the original PR)
- Adds pre-flight working-dir validation in `_run_git` — catches missing dirs before subprocess
- Improves `FileNotFoundError` handling — distinguishes missing git binary from missing working directory
- 6 new tests covering tilde path flows (shadow repo identity, list, diff, restore, working-dir resolution, git env)
- 2 new tests for `_run_git` error classification (invalid dir vs missing git)