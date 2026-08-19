**feat: add hermes backup and hermes import commands**

## Summary

Adds two new CLI subcommands for backing up and restoring Hermes configuration:

### `hermes backup`
Creates a zip archive of the entire `~/.hermes/` directory, including:
- `config.yaml` and `.env` (API keys, settings)
- Skills, skins, plugins
- Sessions and state databases
- Cron jobs, memories, logs
- All profile directories under `profiles/`

**Excludes:**
- `hermes-agent/` (the codebase — re-clone instead)
- `__pycache__/` directories and `.pyc` files
- Runtime PID files (`gateway.pid`, `cron.pid`)

Options:
- `-o / --output` — custom output path (defaults to `~/hermes-backup-<timestamp>.zip`)

### `hermes import <zipfile>`
Restores from a previously created backup zip:
- Validates the zip contains Hermes-specific files before extracting
- Auto-detects and strips `.hermes/` prefix wrapping
- Path traversal protection (rejects entries that escape the target dir)
- Confirmation prompt when overwriting existing config (`--force` to skip)

## Files changed
- **`hermes_cli/backup.py`** (new) — backup and import implementation
- **`hermes_cli/main.py`** — argparse wiring + `cmd_backup`/`cmd_import` dispatch
- **`tests/hermes_cli/test_backup.py`** (new) — 29 tests covering exclusion rules, backup creation, import validation, prefix detection, path traversal blocking, confirmation flow, and full round-trip