**fix(cron): anchor naive schedule timestamps to configured timezone**

## Summary
Naive cron schedule timestamps now fire at the user's wall-clock time even when the configured Hermes timezone differs from the server's local timezone.

**Root cause:** `parse_schedule()` anchored a naive ISO timestamp (e.g. `2026-06-22T20:07:00`) to the **server's local** timezone via `dt.astimezone()`, but the due-check (`get_due_jobs` → `_hermes_now()`) runs in the **configured** Hermes timezone. When the two diverge (a cloud host on UTC with `timezone:` set to something else, or vice-versa), the stored instant lands hours off the user's intent — far enough that one-shots never become due and recurring jobs fire at the wrong time. The ticker stays healthy (heartbeat + success markers fresh) because every tick finds nothing due, which is exactly the silent no-fire reported in #51021 ("ticker alive, no logs, no delivery").

## Changes
- `cron/jobs.py`: anchor naive timestamps to `_hermes_now().tzinfo` so `20:07` means 20:07 on the same clock the scheduler checks against. The legacy `_ensure_aware` path still treats already-stored naive values as server-local for back-compat.
- `tests/cron/test_jobs.py`: 2 regression tests — an invariant (parsed offset == configured-now offset) and an E2E (recent-past one-shot becomes due under a diverging timezone). Both fail on old code, pass on new.

## Validation
| config TZ vs server | before | after |
|---|---|---|
| same / none configured | fires ✓ | fires ✓ |
| diverging (e.g. UTC config on PDT host) | never due ✗ | fires ✓ |

- E2E reproduced the never-due bug and confirmed the fix across past/grace/future cases plus a UTC-config-on-PDT-host case.
- Full `tests/cron/` suite passes (0 failures).

**Why CI never caught it:** the suite runs `TZ=UTC` with no diverging `HERMES_TIMEZONE`, so the two offsets always agreed.

## Infographic

![cron-timezone-fix](https://v3b.fal.media/files/b/0a9f8ab7/Ad97WMAE6ytg00eiVv67u_YyNiyTVK.png)