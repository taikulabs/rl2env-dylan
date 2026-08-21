**fix(gateway): fix matrix read receipts**

Salvage of #10334 by @asheriif onto current main.

## Summary

The Matrix adapter's `send_read_receipt()` calls `client.set_read_markers(...)`, a method that does not exist on the pinned `mautrix>=0.20,<1` client (verified empirically against mautrix 0.21.0). Every read receipt attempt has been raising `AttributeError`, caught by the bare `except Exception` and debug-logged — so read receipts on Matrix have been silently broken.

The real mautrix API provides:
- `set_fully_read_marker(room_id, fully_read, read_receipt)` — sets fully-read marker and read receipt in one request (matches the original intent)
- `send_receipt(room_id, event_id)` — receipt-only fallback

This PR updates `send_read_receipt()` to prefer `set_fully_read_marker`, fall back to `send_receipt`, and retain `set_read_markers` as a final legacy fallback for forward/backward compat.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_matrix.py`