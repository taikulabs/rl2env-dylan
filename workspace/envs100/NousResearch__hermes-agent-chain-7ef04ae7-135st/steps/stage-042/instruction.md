**fix(session-db): enrich NULL session metadata via upsert**

## Summary

Gateway sessions now persist their model and billing metadata instead of leaving it NULL.

**Root cause:** the gateway's `get_or_create_session()` writes a bare session row (source + user_id) *before* the agent exists. The agent's later `create_session()` carries the real `model` / `model_config` / `system_prompt`, but `_insert_session_row` used `INSERT OR IGNORE`, which silently dropped that enrichment because the row already existed. Gateway sessions were left with NULL model and NULL billing metadata.

## Changes

- `hermes_state.py`: `_insert_session_row` switches from `INSERT OR IGNORE` to `INSERT ... ON CONFLICT(id) DO UPDATE` with `COALESCE`. NULL columns (`model`, `model_config`, `system_prompt`, `session_key`, `chat_id`, `chat_type`, `thread_id`, `parent_session_id`, `cwd`) get backfilled by a later writer; values an earlier writer already set are never overwritten (a later bare write with `source='unknown'` cannot clobber a real source/model).
- `tests/test_hermes_state.py`: two regression tests — enrichment-on-conflict and no-overwrite-of-existing.

## Validation

| | Before | After |
|---|---|---|
| Gateway session model field | NULL (enrichment dropped) | backfilled from agent's create_session |
| Existing model overwritten by bare write | n/a | no (COALESCE keeps earlier value) |
| state-DB tests | — | 295/295 pass |
| E2E scenarios (bare→enrich, no-overwrite, fresh create, token-write path) | — | 4/4 pass |

## Credit

Original report and fix direction by @LucidPaths in #5048. That PR's other three claims (alias pricing, cached-agent stale session_id, silent token errors) are already addressed on current `main` — alias pricing is handled by canonical alias pricing keys + `_normalize_anthropic_model_name`, the session_id sync is now agent-driven via `agent_result["session_id"]`, and token-write paths already use `logger.debug`/`logger.warning`. This PR salvages the one remaining live gap.

## Infographic

![Session metadata upsert fix](https://v3b.fal.media/files/b/0aa03b5f/0rmKbzRxca4mPGYUipg7Q_cmCkRwFY.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_hermes_state.py`