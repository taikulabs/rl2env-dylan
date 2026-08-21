**fix(openviking): gate memory writes behind MemoryManager + add viking_forget**

## Summary
Built-in `memory` writes now mirror to external providers only after a write actually commits — and the mirror decision lives behind the `MemoryManager` interface instead of inline in the agent loop.

Root cause: both core memory call sites (`tool_executor.py`, `agent_runtime_helpers.py`) called `on_memory_write(...)` unconditionally after running the built-in tool, so a failed write (store full, no-match replace, injection-blocked, drift) or an approval-staged write still notified providers.

## Changes
- `agent/memory_manager.py`: new `notify_memory_tool_write(result, args, *, build_metadata)` — the single entry point the loop calls. Gates on `success is True and staged is not True` (fails closed), expands single-op/batched shapes, keeps only add/replace/remove, builds per-op metadata + `old_text`, fans out to `on_memory_write`. No `MemoryProvider` ABC change.
- `agent/tool_executor.py` + `agent/agent_runtime_helpers.py`: both call sites collapse to one `notify_memory_tool_write(...)` call. The standalone `agent/memory_write_bridge.py` helper (introduced earlier in this branch) is removed — its logic now lives behind the manager.
- `plugins/memory/openviking/__init__.py`: adds `viking_forget`, an exact-URI delete tool for one OpenViking user memory file (provider-gated via `register(ctx)`, zero core schema footprint). Rejects resources/skills/sessions/dirs/summaries/query-fragment URIs and deprecated `viking://agent/...` paths. Drains add-mirror workers on shutdown.
- Tests rewritten as behavior tests against the manager interface (`tests/agent/test_memory_write_bridge.py`) and updated run_agent fakes to subclass `MemoryManager`.

## Validation
| | Before | After |
|---|---|---|
| Failed/staged write notifies provider | Yes (bug) | No |
| Mirror gating location | Inline in agent loop | Behind `MemoryManager` interface |
| `tests/agent/test_memory_write_bridge.py` + openviking + run_agent | — | 524 passed, 0 failed |

## Attribution
Salvages @ehz0ah's three commits (cherry-picked, authorship preserved via rebase-merge). The interface-boundary restructure is the follow-up commit.

Supersedes/ (@srojk34, already closed), #37351 (@someaka), #12792 (@pty819), #31006 (@0xsir0000).

## Infographic

![mgs-codec](https://v3b.fal.media/files/b/0a9f52c7/5HZVGOGCESOIO1m0ngpu2_QK6zGfhB.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_memory_write_bridge.py`
- `tests/run_agent/test_run_agent.py`