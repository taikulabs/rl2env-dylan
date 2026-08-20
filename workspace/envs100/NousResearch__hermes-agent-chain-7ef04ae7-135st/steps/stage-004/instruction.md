**fix(telegram): detect wedged getUpdates consumer via pending_update_count**

## Summary
Telegram polling now recovers when PTB's getUpdates consumer wedges silently — DMs that were queuing in the Bot API and never reaching handlers now trigger an automatic polling restart.

Root cause: the merged CLOSE-WAIT heartbeat only probes `get_me()`, which uses the general request path and stays healthy while the long-poll consumer is stuck (`updater.running=True` but no updates consumed — observed on WSL2). `get_me()` is structurally blind to a dead consumer; the queue keeps growing and nothing fires.

## Changes
- `plugins/platforms/telegram/adapter.py`: new `_probe_pending_updates()` — probes `get_webhook_info().pending_update_count` from the existing `_polling_heartbeat_loop`, right after the `get_me()` probe succeeds. After **two consecutive** probes that see a non-draining queue while the updater claims to be running, it escalates into the existing `_handle_polling_network_error` recovery ladder. No new restart machinery.
- No-ops in webhook mode, when the updater isn't running, or when a reconnect is already in flight. Single-probe-in-flight updates never trip it (two-strike gate).
- `tests/gateway/test_telegram_pending_update_probe.py`: 6 tests.

## Validation
| | Before | After |
|---|---|---|
| Healthy send path + wedged consumer | undetected forever | restart after 2 stuck probes |
| Single in-flight update | n/a | no false restart (2-strike gate) |
| Webhook mode | n/a | no-op |
| Tests | — | 10/10 (6 new + 4 existing send-path-health) |

Credit to **@gazzumatteo**, who identified `pending_update_count` as the missing liveness signal. This reuses the existing heartbeat + recovery path rather than adding a parallel watchdog.

.

## Infographic

![wedged-poller-watchdog](https://v3b.fal.media/files/b/0aa01780/d3LJvSpug-EqmPgKV8o6b_7cPt0n7c.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_pending_update_probe.py`