**fix(agent): detect truncated streaming tool calls before execution**

## Summary

Salvage of #6776 by @AIandI0x1. .

## Problem

When a streaming response is cut mid-tool-call (connection drop, timeout on large payloads), the accumulated `function.arguments` is invalid/incomplete JSON. The mock response builder defaulted `finish_reason` to `"stop"`, so the agent loop treated it as a valid completed turn and tried to execute tools with broken args.

User experience: "preparing write_file..." appears in the spinner, then the prompt resets with no file written and no error message. Silent data loss.

## Fix

**1. Streaming mock builder (~L4567):** Validates accumulated tool call arguments with `json.loads()` during mock response reconstruction. If any tool call has invalid JSON, sets `finish_reason` to `"length"` instead of `"stop"`.

**2. Thinking-exhausted check (~L7795):** Fixes `_thinking_exhausted` to not short-circuit when tool calls are present — truncated tool calls should not be treated as thinking budget exhaustion.

**3. Truncated tool-call handler (~L7876):** After the existing continuation retry logic (which already skips retries when tool calls are present), catches `finish_reason="length"` with tool calls and returns `partial=True` with a clear error instead of executing broken tools.

## Tests

- `test_truncated_tool_call_args_upgrade_finish_reason_to_length` — streaming mock builder detects invalid JSON and upgrades finish_reason
- `test_length_with_tool_calls_returns_partial_without_executing_tools` — main loop refuses to execute, returns partial error, `handle_function_call` never called
- All 14 TestStreamingApiCall tests pass
- All 18 TestRunConversation tests pass

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_run_agent.py`