**fix(pool): sync Anthropic entry on access_token change, not just refresh_token**

## Summary
The Anthropic `claude_code` credential-pool entry now resyncs from `~/.claude/.credentials.json` when the **access_token** changes, not only when the refresh_token rotates.

Root cause: Claude Code CLI performs a silent access-token re-issue — fresh `access_token`, *same* `refresh_token`. The old guard `file_refresh != entry.refresh_token` was `False` in that path, so the sync was skipped, the pool kept a stale bearer, and every request 401'd until the 5-min exhausted TTL expired. The sibling syncs (`_sync_codex_entry_from_auth_store`, `_sync_xai_oauth_entry_from_auth_store`, `_sync_nous_entry_from_auth_store`) already guard on either token; this one lagged.

## Changes
- `agent/credential_pool.py`: dual-field guard (access OR refresh changed), `file_X or entry.X` fallbacks so a partial credentials file can't blank a field, and the previously-omitted `last_error_reason` / `last_error_message` / `last_error_reset_at` resets — bringing this function to full parity with the Codex/xAI/Nous siblings.
- `tests/agent/test_credential_pool.py`: 4 new behavioral tests (access-only change, refresh change, unchanged no-op, full error-field clear).

## Validation
| | Before | After |
|---|---|---|
| access_token re-issue, same refresh | sync skipped → stale bearer → 401 | sync triggers, bearer updated |
| partial credentials file | n/a | existing fields preserved (no blanking) |
| exhausted entry after fresh tokens | error fields left stale | all `last_error_*`/`last_status_*` cleared |
| `tests/agent/test_credential_pool.py` | — | 85/85 pass |
| E2E (real imports, temp HERMES_HOME) | — | 10/10 assertions pass |

Salvaged from #27880 by @EloquentBrush0x with authorship preserved.

## Infographic
![Anthropic pool sync fix](https://v3b.fal.media/files/b/0aa05c5e/DPQyftrJWABLOfAJdeqrg_Et1w7MJK.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_credential_pool.py`