**fix(streaming): filter <think> blocks from gateway stream consumer**

## Summary

Models like MiniMax emit inline `<think>...</think>` reasoning blocks in their content field. The CLI already suppresses these via a state machine in `_stream_delta`, but the gateway's `GatewayStreamConsumer` had no equivalent filtering — raw think blocks were streamed directly to Discord/Telegram/Slack.

**Root cause:** During streaming, raw deltas flow through `_fire_stream_delta()` → `GatewayStreamConsumer.on_delta()` → accumulated and sent to the platform unfiltered. The agent strips think blocks from the final response (line 10333 in run_agent.py), but the stream consumer already delivered the unstripped version and marked it as `final_response_sent`, so the clean version never gets sent.

## Changes

`gateway/stream_consumer.py`:
- Added `_OPEN_THINK_TAGS` / `_CLOSE_THINK_TAGS` class constants (synced with cli.py and run_agent.py)
- Added `_in_think_block` / `_think_buffer` state tracking in `__init__`
- Added `_filter_and_accumulate()` — state machine that suppresses content between think tags, with:
  - Block-boundary check (tag must be at line start or after whitespace-only prefix) to avoid false positives when models mention `<think>` in prose
  - Partial-tag buffering for tags split across streaming deltas
  - Handles all variants: `<think>`, `<thinking>`, `<THINKING>`, `<thought>`, `<reasoning>`, `<REASONING_SCRATCHPAD>`
- Added `_flush_think_buffer()` for stream end (releases held-back partial tags)
- Wired into `run()`: replaced `self._accumulated += item` with `self._filter_and_accumulate(item)`

`tests/gateway/test_stream_consumer.py`:
- 22 unit tests for `_filter_and_accumulate` covering: plain text passthrough, complete blocks, split tags, all tag variants, prose false-positive safety, partial tag buffering, unclosed blocks, multiline blocks, segment reset preservation
- 1 async integration test verifying think blocks never reach the platform adapter