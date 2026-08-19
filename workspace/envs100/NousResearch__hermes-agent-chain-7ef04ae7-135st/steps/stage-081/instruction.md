**fix(memory/mem0): recall on the current question + stronger search guidance**

## Bug

`prefetch(query)` was not reliably giving the model memory for the question being answered. The old Mem0 prefetch path was tied to a post-turn warm, so first-turn recall could be empty and later turns could surface stale/previous-turn context.

## Changes (Mem0 plugin only)

- Strengthened `mem0_search` guidance so the model knows to use memory before answering prior-context questions, and to run multiple/follow-up searches for multi-hop questions.
- Strengthened the Mem0 system prompt block with the same “use memory before answering context-dependent questions” guidance.
- Added current-query prefetch at turn start: `on_turn_start()` starts a Mem0 search for the user’s current query.
- `prefetch(query)` now consumes the current-query result if ready, or waits up to `_PREFETCH_WAIT_SECS = 1.5` before skipping injection.
- Slow Mem0 search no longer stalls the turn indefinitely; `mem0_search` remains the fallback tool when prefetch is not ready.

The `MemoryProvider` interface and core agent loop stay unchanged.

## Tests

- `tests/plugins/memory/test_mem0_v3.py`
  - prefetch searches the current query
  - first-call recall works without a previous warm
  - turn-start queues current-query recall
  - slow search returns quickly and can be consumed later
  - empty results / circuit breaker behavior stay safe
- `tests/run_agent/test_run_agent.py::TestMemoryProviderTurnStart`
  - preserves the contract that `on_turn_start()` runs before `prefetch_all()`

Latest local verification:

```bash
pytest tests/plugins/memory/test_mem0_v3.py tests/run_agent/test_run_agent.py::TestMemoryProviderTurnStart
# 51 passed
```