**fix: suppress duplicate completion notifications when agent consumes output via wait/poll/log**

## Summary

When the agent calls `process(action='wait')`, `process(action='poll')`, or `process(action='log')` and gets the exited status, the `completion_queue` notification is redundant — the agent already has the output from the tool return value. Previously, the drain loops in CLI and gateway would still inject a `[SYSTEM: Background process completed]` message, causing the agent to receive the same information twice.

**Root cause:** Two independent delivery paths with no coordination:
1. **Tool return path**: `wait()` polls `session.exited` → returns output directly
2. **Notification path**: reader thread → `_move_to_finished()` → `completion_queue` → drain loop → `[SYSTEM: ...]` message

**Fix:** Track session IDs in `_completion_consumed` set on ProcessRegistry when wait/poll/log returns an exited process. Drain loops in cli.py (both idle and post-agent) and gateway watcher skip completion events for consumed sessions. Watch pattern events are never suppressed.

## Files changed
- `tools/process_registry.py` — `_completion_consumed` set + `is_completion_consumed()` method + marking in wait/poll/log
- `cli.py` — two drain loops check consumed set before injecting
- `gateway/run.py` — watcher task checks consumed set
- `tests/tools/test_notify_on_complete.py` — 4 new tests (wait/poll/log marking + running negative case)
- `tests/gateway/test_internal_event_bypass_pairing.py` — add method to _FakeRegistry