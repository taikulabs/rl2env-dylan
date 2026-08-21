**fix(gateway): ignore redelivered /restart after PTB offset ACK fails**

## Summary
`/restart` on Telegram no longer restart-loops when PTB's graceful-shutdown `get_updates` ACK times out — the new gateway process detects and silently drops the redelivered `/restart` instead of processing it again.

Root cause: PTB logs `"Error while calling get_updates one more time to mark all fetched updates ... updates may be received twice"` on shutdown when the final offset-ACK call hits a network timeout. The next gateway then receives the same `/restart` from Telegram and triggers another restart cycle. Reported by a community user where this manifested as `/restart` "getting stuck."

## Changes
- `gateway/platforms/base.py` — add `platform_update_id: Optional[int]` to `MessageEvent`
- `gateway/platforms/telegram.py` — propagate `update.update_id` through `_build_message_event` (text / command / location / media handlers)
- `gateway/run.py` — `_handle_restart_command` writes `.restart_last_processed.json` (platform + update_id + timestamp); new `_is_stale_restart_redelivery()` rejects `/restart` with `update_id <= recorded` inside a 5-minute staleness window
- `tests/gateway/test_restart_redelivery_dedup.py` — 9 new tests

## How the guard behaves

| Scenario | Outcome |
|---|---|
| Fresh `/restart`, no prior marker | Proceeds, writes marker |
| Redelivered `/restart` (same `update_id`) | Silently ignored, returns `""` |
| Newer `/restart` (higher `update_id`) | Proceeds, marker updated |
| Marker > 5 min old | Bypassed (treated as stale/orphaned) |
| Corrupt marker JSON | Bypassed, fresh `/restart` proceeds |
| `/restart` with no `update_id` (CLI, other platforms) | Bypassed, proceeds normally |
| Marker from Telegram, incoming from Discord | Bypassed, proceeds normally |

## Validation
| | Before | After |
|---|---|---|
| Redelivered `/restart` from stale Telegram offset | processes `/restart` again → restart loop | silently dropped, no second restart |
| Fresh `/restart` after guard window (>5 min) | N/A | proceeds normally |
| `/restart` from non-Telegram platforms | unchanged | unchanged |

Targeted test run: `tests/gateway/test_restart_redelivery_dedup.py` + `test_restart_drain.py` + telegram text/reply tests — 52/52 pass.

E2E verified with real imports + isolated `HERMES_HOME` across all 5 scenarios (first restart writes marker, redelivery ignored, fresh update_id proceeds, stale marker bypassed, cross-platform bypass).

## Notes
- The notify file (`.restart_notify.json`, used for "gateway restarted successfully" chat notification) is unchanged and still unlinked after notification. The new dedup marker is a separate file so it can persist past the notification lifecycle.
- Guard only activates for Telegram today — the only platform that currently populates `platform_update_id` and has monotonic cross-session update ordering. Future platforms opting in get defensive idempotency for free by populating the field.
- Does NOT touch the `drop_pending_updates` logic on the Telegram adapter's initial poll (still `True`, as before). This is pure application-level idempotency, defensive against the edge case where that server-side drop doesn't fire.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_restart_redelivery_dedup.py`