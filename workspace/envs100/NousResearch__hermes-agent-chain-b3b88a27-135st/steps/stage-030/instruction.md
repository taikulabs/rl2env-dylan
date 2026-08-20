**fix(approval): heartbeat activity during gateway approval wait**

## Summary

When the agent calls the terminal tool with a dangerous command that needs gateway approval, the agent thread blocks in `tools/approval.py` on `entry.event.wait(timeout=...)`. Before this PR, no activity heartbeats fired during that wait. If the user was slow to respond (or had `approvals.gateway_timeout` set higher than the default 300s), the agent thread sat silent long enough for the gateway's inactivity watchdog (`agent.gateway_timeout`, default 1800s) to kill it — even though the agent was doing exactly the right thing and the user was the one causing the delay.

The fix polls the event in 1s slices and calls `touch_activity_if_due` between slices, mirroring the `_wait_for_process()` pattern in `tools/environments/base.py` that covers the subprocess-waiting side of the same problem.

## Evidence

Community user MRB reported `Stuck on terminal tool` on Discord (April 2026). Their logs show **12 repeated idle-timeout events** with this exact shape:

```
ERROR gateway.run: Agent idle for 1800s (timeout 1800s)
  | last_activity=executing tool: terminal | iteration=X/70 | tool=terminal
```

Events #1, #5, #6 were preceded by Discord approval button clicks where the user took 9-10 minutes to respond. Events #2, #3, #4 were covered by the already-shipped PR #10501 (streaming / concurrent tools / Modal backend heartbeats) — this PR closes the remaining gap in `approval.py`.

## How it works

At the default 10s heartbeat cadence (from `touch_activity_if_due`), a 300s approval wait now pings activity ~30 times, well under the 1800s idle threshold. The polling slice is 1s, so user approvals are still essentially instant.

```python
while True:
    _remaining = _deadline - time.monotonic()
    if _remaining <= 0:
        break
    if entry.event.wait(timeout=min(1.0, _remaining)):
        resolved = True
        break
    if touch_activity_if_due is not None:
        touch_activity_if_due(_activity_state, "waiting for user approval")
```

The lazy `from tools.environments.base import touch_activity_if_due` inside the function avoids any import-order coupling and degrades gracefully if the helper can't be imported.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_approval_heartbeat.py`