**fix(gateway): buffer Telegram media groups to prevent self-interruption**

## Summary
- 
- buffer album items by `media_group_id` so Telegram photo/document/video groups arrive as one logical event
- add a small follow-up cleanup so pending media-group flush tasks are cancelled on adapter disconnect

## Why
Telegram albums arrive as multiple updates with a shared `media_group_id`. Without buffering, Hermes treats later album items as fresh user messages and can interrupt itself while it is still responding to the first image. This change debounces those items briefly and merges their attachments before delivery.

## Follow-up on top
The contributor fix was good. I added one small shutdown hardening commit so `disconnect()` cancels any pending album flush tasks and clears the buffered-event map if shutdown happens inside the debounce window.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_documents.py`