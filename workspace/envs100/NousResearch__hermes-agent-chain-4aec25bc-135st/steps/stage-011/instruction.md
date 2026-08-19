**security: close three dangerous-command detection bypasses (salvage of #11861)**

## Summary
Salvage of #11861 — closes three dangerous-command detection bypasses on current main, inspired by Claude Code 2.1.113's expanded deny rules.

## Bypasses closed
| Bypass | Example that previously slipped through |
|---|---|
| macOS `/private/{etc,var,tmp,home}` paths | `echo x > /private/etc/sudoers` |
| `killall` with SIGKILL / regex | `killall -KILL firefox`, `killall -r 'fire.*'` |
| `find -execdir rm` | `find . -execdir rm {} \;` |

On macOS `/etc`, `/var`, `/tmp`, `/home` are symlinks to `/private/<name>` — a write to `/private/etc/sudoers` works identically to `/etc/sudoers` but bypassed the plain `/etc/` pattern check.

## Design
Extracts a shared `_SYSTEM_CONFIG_PATH` fragment so `/etc/` and its `/private/` mirror stay in sync across all 6 patterns that write into system-config paths. Adding another system-protected path in the future is a one-line edit.

## Salvage notes
3,708 commits stale. Cherry-pick hit three conflicts:
1. `approval.py` module constants — main added `_PROJECT_ENV_PATH` / `_SHELL_RC_FILES` / `_CREDENTIAL_FILES`; PR added `_MACOS_PRIVATE_SYSTEM_PATH` / `_SYSTEM_CONFIG_PATH`. Kept both.
2. `approval.py` DANGEROUS_PATTERNS — main added a `_PROJECT_SENSITIVE_WRITE_TARGET` row; PR upgraded `/etc/` to `_SYSTEM_CONFIG_PATH`. Kept the project-env row and applied the upgrade.
3. `test_approval.py` — main added `TestFailClosedUnderPromptToolkit`; PR added 4 new test classes. Both kept.

## Validation
| | Result |
|---|---|
| `tests/tools/test_approval.py` | 184/184 |
| E2E bypasses now blocked | 12/12 (macOS `/private/etc/*`, 5 `killall` variants, `find -execdir rm`) |
| E2E benign still safe | 8/8 (`killall -l`, `killall -V`, `find -execdir ls`, `grep /etc/passwd`, `cat /etc/hosts`, `ls /private/var/db`, etc.) |

## Source
Claude Code 2.1.113 release notes (Dangerous Path Protection + Enhanced deny rules). Originally scouted in #11861.