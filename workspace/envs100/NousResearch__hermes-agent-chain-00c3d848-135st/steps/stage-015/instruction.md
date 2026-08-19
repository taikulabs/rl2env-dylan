**fix: DeepSeek/Kimi thinking mode requires reasoning_content on ALL assistant messages**

## Problem

DeepSeek V4 thinking mode requires `reasoning_content` on **every** assistant message, not just tool-call turns. The existing fix only covered the tool-call path.

When an assistant message is a plain text reply (no `tool_calls`) and `reasoning` is empty, `_copy_reasoning_content_for_api` skips padding entirely, causing DeepSeek to reject the next request with:

> The reasoning_content in the thinking mode must be passed back to the API.

## Fix

Remove the `source_msg.get("tool_calls") and` guard in `_copy_reasoning_content_for_api` so **all** DeepSeek/Kimi assistant messages get `reasoning_content=""` when needed.

## Changes

- `run_agent.py`: broaden condition from `tool_calls + provider` to just `provider`
- `test_deepseek_reasoning_content_echo.py`: update test to expect padding on plain assistant turns

## Verification

`pytest tests/run_agent/test_deepseek_reasoning_content_echo.py -v` — 21/21 passed.