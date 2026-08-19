**feat: rebrand OpenClaw references to Hermes during migration**

## Summary

Two migration improvements for `hermes claw migrate`:

### 1. Rebrand OpenClaw references to Hermes in migrated content

Replaces OpenClaw brand names with "Hermes" in migrated content so that memory entries, user profiles, SOUL.md, and workspace instructions read as self-referential to the new agent identity.

- **rebrand_text()** function with case-insensitive, word-boundary patterns for:
  - OpenClaw / Open Claw / Open-Claw
  - ClawdBot
  - MoltBot
- Applied to:
  - Memory entries (MEMORY.md, USER.md) during `migrate_memory()`
  - Daily memory entries during `migrate_daily_memory()`
  - SOUL.md during `migrate_soul()`
  - Workspace instructions during `migrate_workspace_agents()`
- `copy_file()` gains an optional `transform` callback for text-based file copies

### 2. Don't auto-archive OpenClaw source directory (salvaged from PR #8192 by opriz)

- **Remove auto-archival from `hermes claw migrate`** — `--yes` was silently archiving the source directory, breaking users who want to run both agents side by side. `hermes claw cleanup` is still available for explicit archival.
- **Skip MESSAGING_CWD when it points inside the OpenClaw source directory** — this was the actual root cause of "agent confusion" after migration. The old workspace path (e.g. `~/.openclaw/workspace`) caused the Hermes gateway to use OpenClaw's workspace as its cwd, picking up OpenClaw's AGENTS.md, MEMORY.md, etc. Uses `Path.is_relative_to()` for robust containment check.

### Bug fix: moldbot → moltbot

Fixed typo across 7 files — the legacy bot name was "MoltBot", not "MoldBot":
- `hermes_cli/claw.py` — directory detection
- `openclaw_to_hermes.py` — config filename lookup
- `test_claw.py` — test fixtures
- 3 docs pages

## Tests

- 7 new tests: 4 unit tests for rebrand_text, 2 integration tests (memory + soul migration), 1 MESSAGING_CWD filtering test
- Removed 6 obsolete tests for the deleted `_offer_source_archival`
- Updated 1 test from archival-assertion to source-preservation assertion
- All 68 affected tests pass (32 migration + 36 claw)

Salvages #8192 (opriz)