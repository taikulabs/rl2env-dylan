**fix(agent): restore safe non-streaming fallback after stream failures**

## Summary

Salvage of PR #3008 by @kshitijk4poor.

Fixes the 2 streaming test failures that have been on main since the streaming retry logic landed in #2980.

## Changes

**Streaming fallback logic:**
- After exhausting transient stream retries, fall back to non-streaming instead of propagating the error
- For any other pre-delivery stream error, also fall back to non-streaming
- Keeps the streaming retry logic from #2980 intact (retry transient errors with fresh connections)

**UX improvement (added on top):**
When a model/provider doesn't support streaming, shows a clean message:
```
⚠  Streaming is not supported for this model/provider. Falling back to non-streaming.
   To avoid this delay, set display.streaming: false in config.yaml
```
Instead of a raw Python error or silent fallback.

## Test results

All 6175 tests pass. The 2 previously-failing streaming fallback tests now pass:
- `test_any_stream_error_falls_back`
- `test_fallback_error_propagates`

New test added: `test_exhausted_transient_stream_error_falls_back`

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_streaming.py`