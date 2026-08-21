**fix(memory): pass session transcript to shutdown_memory_provider on gateway + CLI**

## Summary
Memory providers' `on_session_end` hook now receives the real conversation transcript on both gateway session teardown and CLI exit, instead of an empty list.  .

Salvaged from #15481 (@briandevans) with the CLI sibling site fixed in a follow-up commit.

## The bug
Both teardown paths called `shutdown_memory_provider` with an effectively-empty list:

- **Gateway** (`gateway/run.py`): `agent.shutdown_memory_provider()` — no args, so `on_session_end([])` fired on every provider.
- **CLI** (`cli.py`): `shutdown_memory_provider(getattr(agent, 'conversation_history', None) or [])` — `AIAgent` has no `conversation_history` attribute, so the `or []` branch always fired.

Providers that early-return on empty input (Holographic, Hindsight mid-batch) never persisted the session.  Hindsight specifically buffers turns and only flushes at `retain_every_n_turns` boundaries — any turns held below the modulus at restart/idle-expiry/exit were silently dropped.

## The fix
Both sites now forward `agent._session_messages` — the transcript `AIAgent` maintains and refreshes every turn in `_persist_session` (run_agent.py:3378) and several loop paths.

```python
session_messages = getattr(agent, "_session_messages", None)
if isinstance(session_messages, list):
    agent.shutdown_memory_provider(session_messages)
else:
    agent.shutdown_memory_provider()
```

The `isinstance(..., list)` guard is deliberate — it protects against MagicMock agents (whose attribute access auto-synthesises a child mock) falling through to providers that expect `List[Dict]`, keeping existing test suites green.

## Scope
**Part A of #15165 only** (plus the CLI sibling).  Part B (adding an `on_session_end` implementation to the Hindsight plugin) is a separate concern that benefits from this landing first — without Part A the hook would still receive `[]`.

## Commits
1. `fix(gateway): pass session messages to shutdown_memory_provider` — @briandevans, 
2. `fix(cli): pass session messages to shutdown_memory_provider` — widens the same fix to the CLI exit path; #15481 was gateway-only

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_cli_shutdown_memory_messages.py`