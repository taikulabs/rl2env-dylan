**fix(file_tools): resolve tilde using profile home for file operations**

## Summary
In-process file tools now resolve `~` to the **profile** HOME (`get_subprocess_home()`) instead of the gateway process HOME, so cron jobs and gateway-driven sessions that use tilde paths write to the right directory.

Root cause: `write_file` / `read_file` / `patch` resolved `~` via `os.path.expanduser()` / `Path.expanduser()`, which reads the process `HOME`. Under a gateway (Docker/systemd/s6, profile mode), that HOME differs from the interactive session's profile HOME, so `~/...` expanded to a non-existent path and writes failed with `No such file or directory`.

## Changes
- `tools/file_tools.py`: add `_expand_tilde()` (delegates to `hermes_constants.get_subprocess_home()`, falls back to `os.path.expanduser`); route **all 9** tilde-expansion sites through it — including the two that actually open the file (`_resolve_path_for_task`, `_resolve_base_dir`) and the device/sensitive-path guards.
- `tests/tools/test_file_tools_tilde_profile.py`: 6 unit tests for `_expand_tilde` (incl. `~user` not overridden, `None`-home fallback) + 2 integration tests asserting `_resolve_path_for_task("~/…")` resolves under the profile home, not the process HOME.

## Validation
| | Before | After |
|---|---|---|
| cron `write_file("~/scratch/…")` under gateway | resolves to gateway `$HOME` → fails | resolves to profile HOME ✓ |
| `tests/tools/test_file_tools_tilde_profile.py` | n/a | 8/8 pass |
| `ruff check` on changed files | — | clean |

E2E verified: with `HOME=<gateway>` and `get_subprocess_home()=<profile>`, `_resolve_path_for_task("~/scratch/saber-docs/out.txt")` resolves under `<profile>` and no longer leaks the gateway HOME.

The 3 `tests/tools/test_file_tools.py` failures on macOS are pre-existing (`/tmp` → `/private/tmp` symlink in mock assertions; reproduce identically on clean `origin/main`), unrelated to this change.

## Credit
Salvage of #49251 by @Tranquil-Flow (