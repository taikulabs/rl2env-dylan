**fix(bluebubbles): auto-register webhook with server + crash resilience**

## Summary
Salvage of PR #6592 by @mehmoodosman onto current main.

**Problem:** The BlueBubbles adapter starts a local webhook listener but never registers the webhook URL with the BlueBubbles server via its REST API. Without registration, the BB server doesn't know where to send message events → messages never arrive.

**Fix (from PR #6592):**
- Added `_register_webhook()` in `connect()` — POSTs to `/api/v1/webhook`
- Added `_unregister_webhook()` in `disconnect()` — cleans up on shutdown
- Fixed docs: `hermes gateway logs` → `hermes logs gateway`

**Follow-up improvements:**
- **Crash resilience:** Checks for existing registration before POSTing, so restarts after unclean shutdown don't create duplicate webhooks
- **Status range fix:** Accepts 200-299 (not just 200) for webhook creation — BB may return 201 Created
- **Dedup cleanup:** `_unregister_webhook()` removes ALL matching registrations, cleaning up any orphaned duplicates
- **Code quality:** Extracted `_webhook_url` property and `_find_registered_webhooks()` helper to eliminate duplication
- **17 new tests** covering register, unregister, crash resilience (reuse existing), duplicate cleanup, API failures, URL normalization

## Test Results
- 45/45 BlueBubbles tests pass (28 existing + 17 new)
- Pre-existing failures in `test_approve_deny_commands.py` unrelated to this change

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_bluebubbles.py`