**fix(matrix): warn on clock-skew silent message drops**

## Summary

 — Matrix bot joins rooms but silently drops every incoming message.

The root cause turned out to be **environmental, not a code bug**: the reporter's Debian VM had its system clock set ahead of real time. The startup-grace filter at `_on_room_message` compares `event_ts < self._startup_ts - 5`, and when `time.time()` returns a future value, every legitimate live event from the server looks "older than startup" and gets silently dropped before it can reach the message handler.

The reporter (@Schnurzel700) confirmed this in :

> The current main branch works flawlessly without any of my suggested timestamp hacks. The `event_ts = raw_ts / 1000.0` logic is 100% correct (converting Matrix ms to Python seconds). The bot processes everything perfectly now that I fixed my NTP/system clock.

They explicitly asked for a docs note about NTP since the startup-grace filter and E2EE are both sensitive to clock drift.

## What changed

This is a **defensive diagnostic** so the next user hitting clock skew sees a clear actionable warning instead of silent message drops.

### `gateway/platforms/matrix.py`
- New per-adapter state: `_late_grace_drops`, `_late_grace_skew`, `_clock_skew_warned`.
- In `_on_room_message`, when the grace check drops an event AND we're more than 30 seconds past startup (i.e. past the initial-sync replay window), sample the skew. Drops only count when their skew matches the first sample within 60 seconds — a **constant** offset is the signature of real clock drift, while varied-age backfill from a freshly-invited room would have wildly different skews and resets the sampler.
- After 3 consecutive consistent late drops, emit a one-shot `logger.warning` with the skew value and concrete NTP-fix commands.
- Reset the detector at the top of `connect()` so reconnects after the user fixes NTP rearm the warning cleanly.

### `tests/gateway/test_matrix.py`
5 new tests in `TestMatrixClockSkewWarning`:

| Test | Asserts |
|------|---------|
| `test_late_drops_emit_one_shot_clock_skew_warning` | Reporter's exact scenario (2h clock offset) — warning fires exactly once, counter pinned at 3, skew "7200" in message |
| `test_initial_sync_drops_do_not_warn` | Backfill within 30s of startup is silent (preserves the original grace-filter behavior) |
| `test_fewer_than_three_late_drops_do_not_warn` | Single delayed event isn't enough — needs 3 consecutive |
| `test_varied_backfill_skews_do_not_warn` | 5 events spanning 1h–30d post-startup don't trip the detector (real backfill from invited rooms is excluded) |
| `test_state_reset_allows_warning_to_fire_again` | After the reset block runs, a fresh skew can warn again |

### `website/docs/user-guide/messaging/matrix.md`
New troubleshooting entry "Bot joins rooms but silently drops every message (clock skew)" with the diagnostic log signature to look for and platform-specific NTP-sync commands (`timedatectl set-ntp true` on Linux, `sntp -sS` on macOS).