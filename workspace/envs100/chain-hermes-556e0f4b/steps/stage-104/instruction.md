**fix(api_server): streaming breaks when agent makes tool calls**

## Summary

When the agent makes tool calls during streaming, it fires `stream_delta_callback(None)` to signal the CLI display to close its response box. The API server's `_on_delta` callback was forwarding this `None` directly into the SSE queue, where the SSE writer treats it as end-of-stream and terminates the HTTP response prematurely.

After tool calls complete, the agent streams the final answer through the same callback, but the SSE response was already closed. Open WebUI (and similar frontends) never received the actual answer — they just saw the response "get stuck" during tool calling.

## Fix

Filter out `None` in `_on_delta` so the SSE stream stays open through tool calls. The SSE loop already detects completion via `agent_task.done()`, which handles stream termination correctly without needing the `None` sentinel.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`