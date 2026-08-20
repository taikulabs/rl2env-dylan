**fix(agent): persist tool calls before turn-end flush**

## Summary

 — tool calls execute but aren't persisted to the session DB before the turn-end flush.

`agent/conversation_loop.py` appends the assistant `tool_calls` message and then calls `_execute_tool_calls(...)` with **no `_flush_messages_to_session_db` in between**. If a destructive or process-terminating tool runs during execution, the just-executed `assistant(tool_calls)` block (and any completed tool results) are lost from `state.db` — the session DB is missing the turn that actually ran. Verified still live on current `main`.

The flush layer (`run_agent._flush_messages_to_session_db`) is identity-idempotent (`_flushed_db_message_ids`), so adding mid-turn flushes is safe (no double-writes).

## Fix

- `conversation_loop.py`: flush right after appending the assistant tool_calls block, **before** `_execute_tool_calls`.
- `tool_executor.py`: `_flush_session_db_after_tool_progress()` + per-tool-result flushes in **both** the sequential and concurrent execution paths (including cancelled/skipped results) — so each completed result is persisted before the next dispatch.

## Salvage / attribution

Salvaged from #49528 (@konsisumer), cherry-picked onto current `main`; authored by @konsisumer. The original PR's tests mocked `_invoke_tool`, but the **sequential** path on current main dispatches via `run_agent.handle_function_call` (dispatch-path drift), so those tests were ineffective / failing on main. The tests were **rewritten** (co-authored) to exercise the real dispatch surfaces and pin the ordering contract.

## Tests

`tests/run_agent/test_tool_call_incremental_persistence.py` (rewritten, 3 tests):
- sequential path — mocks the real `handle_function_call`, asserts interleaved `dispatch → flush → dispatch → flush` ordering;
- concurrent path — mocks the real `_invoke_tool`, asserts per-result flush order + growing tool count;
- `run_conversation` E2E — captures the DB snapshot at `_execute_tool_calls` entry and asserts the assistant tool_calls block is already flushed.

All 3 pass; each is mutation-checked (reverting any of the 3 production flush sites fails the corresponding test).

## Whole-bug-class

The two sibling assistant-tool_calls-append sites (`conversation_loop.py:3857` invalid-JSON recovery, `:4407` outer exception backfill) append synthetic/rejected tool_calls that **never reach real tool execution**, so nothing executed-but-unpersisted can be lost there. The one real `_execute_tool_calls` site is now flush-preceded; both dispatch paths flush per-result.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_tool_call_incremental_persistence.py`