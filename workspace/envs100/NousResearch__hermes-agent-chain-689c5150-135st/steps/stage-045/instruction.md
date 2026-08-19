**feat: fix SQLite safety in hermes backup + add --quick snapshots + /snapshot command**

## What this PR does

Three changes consolidated into the existing `hermes_cli/backup.py`:

### 1. Bug fix: SQLite safe copy in `hermes backup`

`hermes backup` previously used raw `zf.write()` for `.db` files. When a database is in WAL mode (which `state.db` always is), raw file copy can produce a corrupted backup. Now uses `sqlite3.Connection.backup()` — the official API for consistent SQLite backups.

### 2. `hermes backup --quick` flag

Fast snapshot of just critical state files, stored locally in `~/.hermes/state-snapshots/`:

```bash
hermes backup --quick                        # snapshot critical state
hermes backup --quick --label before-upgrade  # with a label
```

Auto-prunes to 20 snapshots.

### 3. `/snapshot` slash command (alias `/snap`)

In-session interface for the same quick backup logic:

```
/snapshot                  — list recent snapshots
/snapshot create [label]   — snapshot config.yaml, state.db, .env, etc.
/snapshot restore <id>     — restore state (accepts ID or number)
/snapshot prune [N]        — keep only N most recent (default 20)
```

## Files changed

| File | Change |
|------|--------|
| `hermes_cli/backup.py` | SQLite fix + quick snapshot functions (~200 lines added) |
| `hermes_cli/main.py` | `--quick` and `--label` args on backup parser |
| `hermes_cli/commands.py` | CommandDef for `/snapshot` (alias `/snap`) |
| `cli.py` | Handler + dispatch (~90 lines) |
| `tests/hermes_cli/test_backup.py` | 24 new tests (SQLite safe copy + quick snapshots) |

**Removed:** `tools/state_backup.py` — consolidated into `hermes_cli/backup.py` to avoid a parallel system alongside the existing backup module.

## Design

- **No new modules** — everything in the existing backup module
- **No hooks in `run_agent.py`** — purely on-demand, zero runtime overhead
- **SQLite `backup()` API** for safe state.db copies (credit to @itsXactlY for this approach in #8406)
- **Profile-aware** via `get_hermes_home()`
- **Restore by number** — `/snapshot restore 1` restores the most recent

## What gets snapshotted

| File | Purpose |
|------|---------|
| `state.db` | Session history |
| `config.yaml` | Agent configuration |
| `.env` | API keys |
| `auth.json` | Provider credentials |
| `cron/jobs.json` | Cron definitions |
| `gateway_state.json` | Gateway state |
| `channel_directory.json` | Channel config |
| `processes.json` | Background processes |

## Test results

```
tests/hermes_cli/test_backup.py — 67 passed in 0.19s
tests/hermes_cli/test_commands.py — 104 passed in 0.15s
```

Plus E2E smoke test: create snapshot with WAL-mode state.db → modify config + insert rows → restore → verify original state recovered correctly.

## Replaces

Closes the use case from PRs #8406 and #7813 with ~200 lines of new logic instead of a 1090-line content-addressed storage engine with WAL/branching/auto-hooks.