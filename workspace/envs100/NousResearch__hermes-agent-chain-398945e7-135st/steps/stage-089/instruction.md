**fix(telegram): probe polling liveness after reconnect to detect wedged Updater (salvage #18088)**

After a transient 502/Bad Gateway on `getUpdates`, the Updater can resume with `running=True` but a wedged consumer task — no `getUpdates` progress, no error_callback, and the reconnect ladder stuck at attempt 1 forever. Users see a healthy-looking gateway that silently drops Telegram messages until manual restart.

## What changed
- `gateway/platforms/telegram.py`: after successful `start_polling()` in `_handle_polling_network_error`, schedule `_verify_polling_after_reconnect()` as a background task. The probe sleeps 60s, verifies `Updater.running` is still True, and calls `bot.get_me()` with a 10s timeout (shares the same httpx client — a wedged pool fails this probe). Any failure re-enters the reconnect ladder with the probe's exception, so the existing MAX_NETWORK_RETRIES escalation path becomes reachable.
- `tests/gateway/test_telegram_network_reconnect.py`: 6 new tests covering healthy probe, wedged-Updater, get_me timeout, get_me raises, fatal-state bail, and reconnect-schedules-probe.

## Why this shape
Additive layer — no PTB-internal coupling, no Application rebuild. Happy path unchanged. Wedged path escalates through the ladder like it should, so external supervisors (systemd `Restart=on-failure`) can do their job.

## Validation
- `scripts/run_tests.sh tests/gateway/test_telegram_network_reconnect.py` → 15 passed (9 existing + 6 new).
- E2E: three scenarios against a mocked Updater —
  1. Healthy reconnect schedules exactly one probe task, error_count resets to 0.
  2. Wedged Updater (`get_me` hangs) → probe times out → ladder re-entered with `asyncio.TimeoutError`.
  3. Genuinely healthy probe → no ladder re-entry (no false positive on quiet idle bots).

.