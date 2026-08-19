**feat(update): auto-backup HERMES_HOME before hermes update**

## Summary
Every `hermes update` now creates a full backup zip of HERMES_HOME first, so users can roll back to the exact state they had before the update if anything breaks. Configurable, default on.

## Changes
- `hermes_cli/backup.py`: new `create_pre_update_backup()` — writes `<HERMES_HOME>/backups/pre-update-<stamp>.zip` using the same exclusion rules + SQLite safe-copy as `hermes backup`. Auto-rotates (keeps last N, `pre-update-*.zip` only — hand-dropped zips untouched). `backups/` added to `_EXCLUDED_DIRS` so backups don't nest.
- `hermes_cli/main.py`: `_run_pre_update_backup()` called at the top of `_cmd_update_impl` before any git op. Prints save path, restore command, how to disable. Never blocks the update if the backup fails. New `--no-backup` flag for one-off override.
- `hermes_cli/config.py`: new `updates` section in `DEFAULT_CONFIG` — `pre_update_backup: true`, `backup_keep: 5`. Auto-surfaces in the dashboard config UI.
- Tests: +11 covering location, content parity with `hermes backup`, no-recursion, rotation, manual file preservation, config gate, flag override.

## User-facing output
```
⚕ Updating Hermes Agent...

◆ Creating pre-update backup...
  Saved:    ~/.hermes/backups/pre-update-2026-04-27-053104.zip (142 MB, 8.3s)
  Restore:  hermes import ~/.hermes/backups/pre-update-2026-04-27-053104.zip
  Disable:  set updates.pre_update_backup: false in config.yaml
            (or pass --no-backup on a single update)
```

## Validation
| | Result |
|---|---|
| `scripts/run_tests.sh tests/hermes_cli/test_backup.py` | 81/81 passed |
| E2E: backup location, no-recursion, rotation, flag/config gates | verified against isolated HERMES_HOME |
| `hermes update --help` | shows `--no-backup` flag |
| Dashboard config UI | `updates.pre_update_backup` + `updates.backup_keep` auto-appear |