**fix(cli): buffer reasoning preview chunks and fix duplicate display**

## Summary

Three improvements to reasoning/thinking display in the CLI:

**1. Buffer tiny reasoning chunks.** Providers like DeepSeek stream reasoning one word at a time, producing a separate `[thinking] word` line per token. Adds a buffer that coalesces chunks and flushes at natural boundaries (newlines, sentence endings, terminal width).

**2. Fix duplicate reasoning display.** Centralizes callback selection into `_current_reasoning_callback()` — one method instead of 4 scattered inline ternaries. Prevents the streaming box and preview callback from firing simultaneously.

**3. Fix post-response reasoning box guard.** Changes check from `not self._stream_started` to `not self._reasoning_stream_started`, so the final reasoning box is only suppressed when reasoning was actually streamed live.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_reasoning_command.py`