**feat(backup): exclude SQLite WAL/SHM/journal sidecars**

## Summary
`hermes backup` now skips `*.db-wal`, `*.db-shm`, and `*.db-journal` files. The backup already takes a consistent snapshot of each `*.db` via `sqlite3.backup()`; shipping the live sidecars alongside pairs a fresh snapshot with stale WAL state and produces a torn restore on first open.

## Changes
- `hermes_cli/backup.py`: `.db-wal`, `.db-shm`, `.db-journal` added to `_EXCLUDED_SUFFIXES` with a comment explaining why
- `tests/hermes_cli/test_backup.py`: new `test_excludes_sqlite_sidecars` confirming the sidecars are excluded but the parent `*.db` is still included

## Validation
| | Before | After |
|---|---|---|
| `state.db-wal` / `state.db-shm` in zip | included (stale, torn) | excluded |
| `state.db` | safe-copied, included | safe-copied, included (unchanged) |
| `tests/hermes_cli/test_backup.py` | 85 passed | 86 passed |