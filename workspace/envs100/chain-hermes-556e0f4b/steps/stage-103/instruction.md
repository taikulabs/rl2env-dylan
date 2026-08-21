**feat: persist reasoning across gateway session turns (schema v6)**

## Summary

Adds `reasoning TEXT` and `reasoning_details TEXT` columns to the `messages` table (schema v5→v6). This preserves assistant reasoning chains across gateway session reloads so providers that replay reasoning receive coherent multi-turn context.

## Problem

Three reasoning fields exist on in-memory assistant messages:
- `msg["reasoning"]` — plain text (DeepSeek, Qwen, Moonshot, Novita)
- `msg["reasoning_details"]` — structured array from OpenRouter (opaque objects with signatures)
- `msg["codex_reasoning_items"]` — encrypted blobs for OpenAI Codex Responses API

All three flow correctly within a single CLI session. The existing provider-compatibility code at `run_agent.py:5673-5696` already converts `reasoning` → `reasoning_content` and preserves `reasoning_details` for the API.

**None of these were persisted to the session DB.** On gateway reload, all reasoning was lost. The `messages` table had no columns for any of them.

## Changes

**`hermes_state.py`** — Schema v6:
- Add `reasoning TEXT` and `reasoning_details TEXT` columns to messages table
- Auto-migration via `ALTER TABLE ADD COLUMN` (backward-compatible)
- `append_message()` accepts `reasoning` and `reasoning_details` params
- `get_messages_as_conversation()` restores them on assistant messages only
- `reasoning_details` is JSON-serialized for storage

**`run_agent.py`** — `_flush_messages_to_session_db()`:
- Pass `reasoning` and `reasoning_details` for assistant messages

**`gateway/run.py`** — agent_history builder:
- Preserve reasoning fields on non-tool-calling assistant messages (tool-calling messages already passed through all fields via the `{k: v for k, v in msg.items() if k != "timestamp"}` path)

**`gateway/session.py`** — `append_to_transcript()` and `rewrite_transcript()`:
- Pass reasoning fields through to the DB

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_hermes_state.py`