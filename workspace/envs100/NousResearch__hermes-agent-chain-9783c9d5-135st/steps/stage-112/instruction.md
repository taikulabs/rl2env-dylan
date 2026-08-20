**feat(api_server): stream tool progress to Open WebUI**

## Summary

Streams tool progress messages to Open WebUI during SSE streaming, so users see what the agent is doing while tools execute (e.g. `` `💻 ls -la` ``).

Inspired by #4032 (by @sroecker), reimplemented cleanly to avoid breaking the existing callback contract.

## What changed

**`gateway/platforms/api_server.py`** (+14 lines):
- Added `tool_progress_callback` parameter through `_create_agent()` and `_run_agent()`
- Added `_on_tool_progress(name, preview, args)` callback in the streaming handler that formats progress as inline markdown and puts it in the SSE stream queue
- Skips internal events (tool names starting with `_`)

**No changes to `run_agent.py`** — uses the existing `tool_progress_callback` with its current 3-arg signature that fires at tool start. This is the key difference from #4032 which modified the callback signature with 6 positional args, breaking CLI and gateway consumers.

## Why #4032 couldn't be merged

The original PR added new `self.tool_progress_callback(name, msg, args, "complete", duration, result)` calls (6 positional args) throughout `run_agent.py`. The existing consumers only accept 3 args:
- CLI: `_on_tool_progress(self, function_name, preview, function_args)`
- Gateway: `progress_callback(tool_name, preview=None, args=None)`

This would crash both CLI and gateway with `TypeError` whenever a tool completed.

## Tests

2 new tests in `tests/gateway/test_api_server.py`:
- `test_stream_includes_tool_progress` — verifies progress appears in SSE stream
- `test_stream_tool_progress_skips_internal_events` — verifies `_thinking` events are filtered

All 2574 gateway + CLI tests pass.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`