**feat(gateway): suppress home-channel shutdown broadcast on flagged drains**

## Infographic

![drain-quiet-shutdown](https://v3b.fal.media/files/b/0aa03a7e/c4o-3Yy4C8ail21nimMPi_EhXxFoqQ.png)

## What & why

When a gateway shuts down it broadcasts a `⚠️ Gateway shutting down` message to every configured **home channel** (and to every active session). That's fine for a one-off restart — but with auto-update now always-on for the eligible Hermes Cloud fleet, an instance can be image-migrated multiple times a day. Each migration SIGTERMs the old gateway → fires the home-channel broadcast → users get spammed with operator-flavoured "gateway restarting" noise dozens of times a day.

This adds a generic **`suppress_notification`** boolean to the drain-request marker. When a drain that ends in process exit is flagged (NAS sets it on the auto-update / image-migration drain — a follow-up PR), the gateway skips **only** the home-channel broadcast.

The **per-active-session interrupt ping is always kept**: on a drained shutdown it's empty by construction (the drain waited for `active_agents == 0`), and in the force-interrupt / deadline-exceeded case it carries the genuinely useful "your task was cut off, send a message and I'll resume" hint.

## Design notes

- **Generic flag, not a `kind` enum.** The gateway stays agnostic about *why* a drain is quiet — it just obeys "be quiet this time." The policy of which drain causes set the flag lives entirely in the caller (NAS), at the call sites where the cause is actually known.
- **Default-false → fully backwards compatible.** A marker written without the field, a legacy marker, or any operator-initiated drain behaves exactly as today (the broadcast still fires). The flag only ever *adds* suppression for a marker that explicitly opts in.
- **Reuses the NS-570 epoch-staleness check.** `drain_notification_suppressed()` honours the flag only for a marker stamped with the *current* instantiation epoch — so an orphaned marker that survived a machine restart on the durable `HERMES_HOME` volume can never silence a fresh gateway's legitimate shutdown broadcast.
- **Never raises.** A malformed/half-written marker reads as "not suppressed" — failing toward the louder, more-visible behaviour.

## Changes

- `gateway/drain_control.py` — `write_drain_request()` gains `suppress_notification` (default `False`); new `drain_notification_suppressed()` reader (current-epoch + truthy flag); contract docstring updated.
- `hermes_cli/web_server.py` — `POST /api/gateway/drain` reads the flag from the body, passes it to the writer, echoes it in the response.
- `gateway/run.py` — `_notify_active_sessions_of_shutdown()` skips **only** the home-channel broadcast loop when the flag is active; the active-session ping path is untouched.

## Tests

12 new tests (`tests/gateway/test_external_drain_control.py`, `tests/gateway/test_restart_drain.py`, `tests/hermes_cli/test_web_server.py`); full involved suites green (399 passed):

- flag round-trips through writer + reader + HTTP endpoint;
- home-channel broadcast suppressed when the flag is set, **active-session ping still fires**;
- both fire when the flag is absent (today's behaviour preserved);
- stale-epoch / legacy / corrupt markers never suppress (the NS-570 analogue for suppression).

The home-channel suppression test was proven RED with the `run.py` gate neutered (2 sends — the home channel leaked through) before being made green by the fix.

This is the hermes-agent half of the change; the NAS caller that sets the flag on the auto-update drain ships separately.