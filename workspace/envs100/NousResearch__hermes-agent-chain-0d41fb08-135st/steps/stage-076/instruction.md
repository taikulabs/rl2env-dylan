**fix: propagate child activity to parent during delegate_task**

## Summary

Fixes the gateway inactivity timeout firing during `delegate_task` execution. When a subagent runs, the parent agent's activity tracker freezes because `child.run_conversation()` blocks synchronously and the child's own `_touch_activity()` never propagates back to the parent. The gateway polls the parent's `seconds_since_activity`, sees it growing, and fires a spurious 'No activity for 15 min' warning — eventually killing the agent at the 30-min timeout even though the subagent is actively working.

**Reported by community user Josh on Discord** — running delegate_task from Telegram, getting inactivity warnings while subagent actively iterates.

## Changes

**`tools/delegate_tool.py`:**
- Added a heartbeat daemon thread in `_run_single_child()` that calls `parent._touch_activity()` every 30 seconds (configurable via `_HEARTBEAT_INTERVAL`)
- Heartbeat reads the child's `get_activity_summary()` and propagates rich detail: current tool, iteration count, last activity description
- Thread starts before `child.run_conversation()` and is stopped + joined in the `finally` block (handles both success and error paths)
- Thread-safe: `_touch_activity` only sets two attributes (atomic under GIL)

**`tests/tools/test_delegate.py`:**
- 4 new tests in `TestDelegateHeartbeat`:
  - Heartbeat fires and touches parent activity during child execution
  - Heartbeat stops after child completes (no leak)
  - Heartbeat stops after child error (no leak)
  - Heartbeat includes `last_activity_desc` when no tool is active

## Impact

- Gateway users running `delegate_task` no longer get spurious inactivity warnings
- 'Still working...' status messages now show what the subagent is doing (e.g., 'delegate_task: subagent running terminal (iteration 5/50)') instead of just 'running: delegate_task'
- Zero impact on CLI (no inactivity timeout there)
- Zero impact on non-delegate tool calls

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_delegate.py`