**fix: scope tool interrupt signal per-thread to prevent cross-session leaks**

## Summary

The interrupt mechanism in `tools/interrupt.py` used a **process-global** `threading.Event`. In the gateway, multiple agents run concurrently in the same process via `run_in_executor`. When any agent was interrupted (user sends a follow-up message), the global flag killed **ALL** agents' running tools — terminal commands, browser ops, web requests — across all sessions.

### What changed

| File | Change |
|------|--------|
| `tools/interrupt.py` | Replace global `threading.Event` with a set of interrupted thread IDs. `set_interrupt()` targets a specific thread; `is_interrupted()` checks the current thread. Backward-compat `_ThreadAwareEventProxy` for legacy `_interrupt_event` usage. |
| `run_agent.py` | Store execution thread ID at start of `run_conversation()`. `interrupt()` and `clear_interrupt()` scope to that thread only. |
| `tools/code_execution_tool.py` | Use `is_interrupted()` instead of `_interrupt_event.is_set()` |
| `tools/process_registry.py` | Same — use `is_interrupted()` |
| Tests | Updated for per-thread semantics + new `TestPerThreadInterruptIsolation` verifying cross-thread isolation |

### The bug

1. User A is chatting on Telegram — agent runs `pip install` (terminal tool)
2. User B sends a follow-up message to their own session
3. Gateway calls `agent_B.interrupt()` → `_set_interrupt(True)` → sets **global** flag
4. User A's terminal tool poll loop: `is_interrupted() → True` → kills `pip install`
5. User A's agent gets `[Command interrupted]` — work destroyed

### The fix

Each agent records its executor thread ID when `run_conversation()` starts. `interrupt()` and `clear_interrupt()` pass this thread ID to `set_interrupt()`, which only marks **that specific thread** as interrupted. `is_interrupted()` checks `threading.current_thread().ident` — each thread only sees its own interrupt state.