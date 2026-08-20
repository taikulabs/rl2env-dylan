**fix(signal): skip contentless envelopes (profile key updates, empty messages)**

## What does this PR do?

Signal-cli sends `dataMessage` wrappers for profile key updates and other metadata events that have no actual text content. These were reaching the gateway as `msg=""` and triggering full agent turns for nothing — wasting LLM calls on events like a contact changing their display picture.

Add an early return in `_handle_envelope()` when both the message field is empty/missing/whitespace AND there are no attachments. Messages with media attachments but no text still flow through normally.

## Related Issue

No existing issue. Observed in gateway logs: profile key update from a contact triggered `msg=""` inbound and a full agent run.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_signal.py`