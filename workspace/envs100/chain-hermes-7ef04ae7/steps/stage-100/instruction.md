**fix(telegram): recover when polling updater stops while process stays alive**

## Summary

The Telegram polling watchdog now recovers when PTB's `Updater` stops entirely while the process stays alive — closing the silent-death gap in #55769.

Root cause: `_probe_pending_updates` (the heartbeat's stuck-consumer probe) treated `updater.running == False` as "someone else's job" — it reset its counter and returned. But `get_me()` on the general request path stays healthy when the long-poll task is simply gone, so neither PTB's `error_callback` nor the connectivity heartbeat ever fires. Result: process alive (systemd green, threads healthy), send path fine, polling dead indefinitely, zero logs.

## Changes
- `plugins/platforms/telegram/adapter.py` — `_probe_pending_updates`: detect `updater.running == False` (no reconnect in flight) as a dead poller and escalate through the existing `_handle_polling_network_error` recovery ladder after two consecutive probes. Adds `_polling_not_running_count` debounce; moves the in-flight-reconnect guard ahead of the updater check so its transient `stop()` → `start_polling()` window can't be misread as a dead updater. No new config keys, no new env vars, no new restart machinery.
- `tests/gateway/test_telegram_pending_update_probe.py` — replaces the test encoding the old "stopped updater = no-op" assumption with coverage for: single stopped probe doesn't escalate, two consecutive stopped probes trigger recovery, a recovered (running) updater resets the counter, and an in-flight reconnect suppresses escalation.

## Validation
| | Before | After |
|---|---|---|
| Updater stopped, process alive | watchdog silent forever | recovers after 2 probes (~3 min) via existing ladder |
| `_probe_pending_updates` tests | old no-op assumption | 9/9 pass |
| E2E on current main | — | stopped→recovery, running-resets, in-flight-suppressed all verified |

Salvage of #55789 by @PRATHAMESH75 — cherry-picked onto current `main`, authorship preserved.

## Infographic

![PR #55789 infographic](https://v3b.fal.media/files/b/0aa06c93/dMz-WiIavlywmZielTu5D_4BNMI3L4.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_pending_update_probe.py`