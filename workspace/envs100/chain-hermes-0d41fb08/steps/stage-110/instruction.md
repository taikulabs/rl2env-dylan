**fix(gateway): preserve queued voice events for STT**

## Summary

Fixes a bug where voice messages that arrive while the agent is busy (queued/interrupted) lose their STT transcription. The gateway's `_dequeue_pending_text()` was stripping `MessageEvent` objects down to plain text, so voice-only events got reduced to a placeholder like `[User sent audio: /path]` that completely bypassed the STT preprocessing path.

## Changes
- `_dequeue_pending_text()` → `_dequeue_pending_event()`: returns full `MessageEvent` instead of text-only
- Extracts inbound message preprocessing (sender attribution, vision, STT, documents, reply context, @ references) into shared `_prepare_inbound_message_text()` method
- Both normal and queued re-entry paths now use the same preprocessing pipeline
- Queued events preserve media metadata, source identity, and message ID through re-entry
- Recursion-depth-cap re-queue uses `merge_pending_message_event()` to preserve full event

## Tests
- 12 passed in test_queue_consumption.py + test_stt_config.py
- 180 passed, 7 pre-existing failures (confirmed same on main), 21 skipped across the full targeted gateway regression set

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_queue_consumption.py`
- `tests/gateway/test_stt_config.py`