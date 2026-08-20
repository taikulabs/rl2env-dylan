**fix(telegram): recover when polling updater stops while process stays alive**

## Summary

The Telegram gateway can silently stop receiving messages while the process stays alive (systemd green, threads healthy, send path fine) — no logs, no errors — until manually restarted. This makes the gateway self-heal from that state.

Root cause: the polling heartbeat's `_probe_pending_updates` already handled a *wedged-but-running* long-poll consumer, but treated a fully **stopped** updater (`running == False`, no reconnect in flight) as "someone else's job" — it reset its counter and returned. Because `get_me()` on the general request path stays healthy, neither PTB's `error_callback` nor the connectivity heartbeat ever fires. Result: process alive, send path fine, polling dead, indefinitely.

## Changes

- `plugins/platforms/telegram/adapter.py` — `_probe_pending_updates` now detects `updater.running == False` and feeds it into the **existing** `_handle_polling_network_error` recovery ladder (stop → drain pool → `start_polling`). Debounced over two consecutive probes via a new `_polling_not_running_count`. The in-flight-reconnect guard is moved ahead of the updater check so the reconnect's own transient `stop()`→`start_polling()` window (where `running` is briefly False) can't false-trip. No new restart machinery, no new config keys, no new env vars.
- `tests/gateway/test_telegram_pending_update_probe.py` — replaced the test that encoded the old buggy "stopped updater = no-op" assumption with coverage for: single stopped probe does not escalate, two consecutive stopped probes trigger recovery, a recovered (running) updater resets the counter, and an in-flight reconnect suppresses escalation.

## Validation

| | Before | After |
|---|---|---|
| Updater stops (`running=False`) | watchdog blind, silent forever | detected, routed into recovery ladder |
| Reconnect-in-flight stop/start window | (n/a — never reached) | guarded first, no false trip |
| Targeted tests | — | 9/9 pass |
| Sibling reconnect/polling tests | — | 62/62 pass |

Salvaged from @PRATHAMESH75's PR #55789, cherry-picked onto current `main` with authorship preserved.

## Infographic

![Telegram polling self-heal](https://v3b.fal.media/files/b/0aa06d4a/5Z_HmqS_1-ukrklbJ-gTA_FTzcnSsf.png)

Nous Research

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_infinite_compaction_loop.py`