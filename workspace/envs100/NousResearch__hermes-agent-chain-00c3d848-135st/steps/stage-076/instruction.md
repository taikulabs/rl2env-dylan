**feat(update): make pre-update backup opt-in (off by default)**

## Summary
`hermes update` no longer runs a full HERMES_HOME zip backup on every invocation — the backup was adding minutes to every update on large homes. Opt in per run with `--backup`, or set `updates.pre_update_backup: true` in config.yaml to restore the old behavior.

## Changes
- `hermes_cli/config.py`: `updates.pre_update_backup` default `True` → `False`, doc comment rewritten
- `hermes_cli/main.py`: new `--backup` flag on `hermes update` (opposite of existing `--no-backup`); silent no-op when disabled so there's no output spam on every update; `--no-backup` still wins if both are passed
- `tests/hermes_cli/test_backup.py`: updated `TestRunPreUpdateBackup` — covers default-off (silent), `--backup` opt-in, explicit config-enabled path, and the `--no-backup` override

## Validation
| | Before | After |
|---|---|---|
| `hermes update` on default config | Runs full zip every time (minutes) | No-op, silent |
| `hermes update --backup` | n/a | Forces backup for this run |
| `hermes update --no-backup` | Skips | Still skips |
| `updates.pre_update_backup: true` in config | Runs backup | Runs backup (unchanged) |
| `tests/hermes_cli/test_backup.py` | 82 passed | 83 passed |

No config version bump needed — deep-merge picks up the new default for existing users who don't have the key set.