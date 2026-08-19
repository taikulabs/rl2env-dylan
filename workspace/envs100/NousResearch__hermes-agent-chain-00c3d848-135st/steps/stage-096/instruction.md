**fix(state): declarative column reconciliation for stuck-at-old-v7 DBs**

Salvage of #14097 (@kshitijk4poor) onto current main.

## Summary
Replaces the version-gated ADD COLUMN chain in `hermes_state.py` with a declarative `_reconcile_columns()` that diffs `SCHEMA_SQL` against `PRAGMA table_info` on every startup and ALTERs in any missing column. Heals the stuck-at-old-v7 scenario from  where `reasoning_content` was silently skipped for users already past version 7 from the pre-renumber `api_call_count` migration.

## What's different from the original PR
Original was 969 commits stale and predated #16651's v10 trigram FTS migration. That migration isn't a column add — it backfills existing messages into the FTS virtual table — so this salvage keeps a single version-gated block for v10 while handing all column additions to `_reconcile_columns()`. Also auto-heals the v9 `codex_message_items` column (stale-missed by the original branch).

## Validation
| Scenario | Result |
|---|---|
| Fresh install | Creates at v10 with all columns |
| Ancient v1 DB | Migrates to v10 with every declared column |
| Stuck-at-old-v7 (the bug) | Adds `reasoning_content` + `codex_message_items`, bumps to 10 |
| v9 DB | v10 trigram FTS backfill runs correctly (2 rows backfilled) |
| Idempotent reopen | No double-backfill |
| `tests/test_hermes_state.py` | 191 passed (includes 3 new regression + invariant tests) |

Credit: @kshitijk4poor