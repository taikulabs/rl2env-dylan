**feat: add post-migration cleanup for OpenClaw directories**

## Summary

After migrating from OpenClaw, leftover workspace directories (`~/.openclaw/workspace/`, etc.) contain state files (todo.json, sessions, logs) that confuse the Hermes agent. It discovers them and reads/writes to stale locations instead of the Hermes state directory, causing issues like cron jobs reading a different todo list than interactive sessions.

Reported by SteveSkedasticity in Discord — three separate `todo.json` files across `~/.hermes/`, `~/.openclaw/workspace/`, and `~/.openclaw/workspace-assistant/` caused the morning check-in cron to read tasks from the wrong location.

## Changes

### `hermes claw migrate` — post-migration archival
- After successful migration (non-dry-run with items migrated), offers to rename the source directory to `.openclaw.pre-migration`
- With `--yes` flag, archives automatically
- Shows state files found in workspace directories before prompting
- Rename only, not delete — user can undo with `mv`

### `hermes claw cleanup` — new subcommand
- Scans for all OpenClaw directories (`~/.openclaw`, `~/.clawdbot`, `~/.moldbot`)
- Shows workspace directories and their state files
- `--dry-run` to preview, `--yes` to skip prompts, `--source` for specific directory
- Alias: `hermes claw clean`

### Migration notes
- Updated `generate_migration_notes()` with prominent "Archive the OpenClaw Directory" section
- Added `hermes claw cleanup` to the post-migration steps list

### Tests
- 42 tests covering: directory discovery, state file scanning, archival (including edge cases), routing, cleanup command, integration with migrate command

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_claw.py`