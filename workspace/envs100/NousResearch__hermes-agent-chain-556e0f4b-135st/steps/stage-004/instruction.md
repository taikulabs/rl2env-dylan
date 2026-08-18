**fix: thread safety for concurrent subagent delegation**

## Summary

Salvage of PR #1471 by @peteromallet — thread safety fixes for concurrent subagent delegation.

### The problem

Running 3+ subagents concurrently via `delegate_task` in batch mode causes segfaults, data corruption, and intermittent crashes from four distinct race conditions.

### Fixes

**1. Remove `redirect_stdout`/`redirect_stderr` from delegate_tool**
`contextlib.redirect_stdout` mutates the global `sys.stdout`. When multiple child agents start concurrently in a `ThreadPoolExecutor`, the race between redirect and the spinner thread corrupts the file descriptor, causing segfaults. The redirect was redundant — children already run with `quiet_mode=True`.

**2. Split agent construction from execution**
`_run_single_child()` → `_build_child_agent()` (main thread, serial) + `_run_single_child()` (worker thread, parallel). `AIAgent` construction creates httpx clients and initializes SSL contexts, which are not thread-safe to do concurrently.

**3. Add `threading.Lock` to `SessionDB`**
Subagents share the parent's `SessionDB` and call `create_session()`, `append_message()`, etc. from worker threads with no synchronization. Every database-accessing method is now wrapped in `with self._lock:`.

**4. Add `_active_children_lock` to `AIAgent`**
`interrupt()` iterates `_active_children` while worker threads append/remove children. Now copies the list under lock before iterating.

**5. Add `_client_cache_lock` to `auxiliary_client`**
Multiple subagent threads may resolve auxiliary clients concurrently via `call_llm()`. Double-checked locking pattern prevents duplicate client creation.

### What was NOT included from the original PR

- Per-task `model`/`provider` overrides in `delegate_task` schema (feature addition, not a safety fix)
- `resolve_provider_credentials()` helper (utility, not needed for the safety fixes)
- `_apply_provider_credentials()` extraction in `run_agent.py` (refactoring, not a safety fix)

### Files changed

| File | Change |
|------|--------|
| `tools/delegate_tool.py` | Split build/run, remove redirect, use lock |
| `hermes_state.py` | Add `threading.Lock` to all DB methods |
| `run_agent.py` | Add `_active_children_lock`, use in `interrupt()` |
| `agent/auxiliary_client.py` | Add `_client_cache_lock`, double-checked locking |
| 6 test files | Update for new `_run_single_child` signature + add `_active_children_lock` |

### Tests

Full suite: 4911 passed, 8 pre-existing failures (unrelated), 200 skipped.

## Credit

Original implementation by @peteromallet (PR #1471).