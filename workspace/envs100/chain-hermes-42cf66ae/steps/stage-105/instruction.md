**fix(gateway): cancel active runs during shutdown**

## Summary
- track background message-processing tasks spawned by platform adapters
- interrupt running agents and cancel adapter background tasks during gateway shutdown before adapters disconnect
- clear shutdown-time pending session state and add regression coverage for restart/shutdown behavior

## What this addresses
Issue #1414 reports that after stopping a busy gateway and restarting with `hermes gateway run --replace`, the old task can appear to keep going, task/progress labels can flicker, and the restarted gateway can fall into a bad state while the previous in-flight work is still unwinding.

I did not reproduce the exact OpenRouter 502 sequence deterministically, but I did isolate a concrete shutdown bug on current main:
- platform adapters spawn background message-processing tasks and do not track them
- `GatewayRunner.stop()` disconnects adapters but does not cancel those tasks
- `GatewayRunner.stop()` also does not interrupt agents already recorded in `_running_agents`

That means an old gateway instance can keep working on in-flight message tasks during shutdown/replacement instead of being cleanly quiesced first.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_gateway_shutdown.py`