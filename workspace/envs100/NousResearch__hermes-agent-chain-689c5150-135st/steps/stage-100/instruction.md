**fix(interrupt): preserve pre-start terminal interrupts**

## Summary

Fixes a race condition where user interrupts arriving before `run_conversation()` binds `_execution_thread_id` are silently lost — the interrupt targets the caller's thread instead of the agent's execution thread, then gets cleared at startup.

## The Bug

1. Gateway starts agent on Thread A → `run_conversation()` begins
2. User sends new message → gateway on Thread B calls `agent.interrupt()`
3. `_execution_thread_id` is still `None`, so `_set_interrupt(True, None)` falls back to `threading.current_thread().ident` → marks **Thread B** (wrong thread)
4. Thread A reaches startup, calls `clear_interrupt()` → clears everything. Interrupt lost.
5. Result: agent keeps running, CLI appears frozen.

## Fix

- `interrupt()`: When `_execution_thread_id` is None, defers thread-scoped signal via `_interrupt_thread_signal_pending` flag instead of targeting caller's thread
- `run_conversation()` startup: After setting `_execution_thread_id`, checks for pending interrupts and binds them to the correct thread instead of blindly clearing
- `clear_interrupt()`: Guards `_set_interrupt(False, ...)` behind `_execution_thread_id is not None`

## Test Results

- 7 passed in `test_interrupt_propagation.py` (including new `test_prestart_interrupt_binds_to_execution_thread`)
- 11 passed in `test_run_agent.py -k interrupt`
- 4 E2E tests validating the race condition fix