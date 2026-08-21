**fix(gateway): keep typing indicator alive across slow send_typing calls**

## Summary

Keeps the Telegram/Discord/etc. typing indicator alive when an upstream provider stall (e.g. Anthropic capacity blip pushing first-token past the 120s stream-read timeout) also slows the platform's typing API round-trip. Before this PR, a single slow `send_typing` call would stall the refresh loop inside its `await`, the platform-side 5s typing expiry would win, and the bubble would vanish right when the user most needs the "still working" signal.

## Root cause

`BasePlatformAdapter._keep_typing` awaited `send_typing` unconditionally. Each call is an HTTP round-trip to the platform API. Under upstream network instability, individual round-trips can take 5-30s; the next scheduled refresh can't fire until the stuck one returns.

## Changes

- `gateway/platforms/base.py` — wrap each `send_typing` in `asyncio.wait_for` with a per-tick timeout derived from `interval` (1.5s cap, always below the 2s cadence). Slow calls are abandoned; the next scheduled tick fires a fresh call. Also catch non-timeout exceptions so one bad tick doesn't kill the whole loop.
- `tests/gateway/test_keep_typing_timeout.py` — 4 new tests:
  - Slow send_typing does not block the refresh cadence (the regression guard — fails without the fix).
  - Fast send_typing still completes normally (timeout is upper bound, not cap).
  - send_typing exception doesn't terminate the loop.
  - Paused-chat regression guard (existing behavior preserved).

## Validation

| | Before | After |
|---|---|---|
| 3s of slow send_typing (10s each), interval=1.0 | 1 start (still stuck) → bubble dies | ≥2 starts, loop on-schedule |
| send_typing raises RuntimeError on tick 1 | loop exits | loop continues ticking |
| Normal fast send_typing | awaited | awaited |
| Paused chat | skipped | skipped |

```
$ scripts/run_tests.sh tests/gateway/test_keep_typing_timeout.py
4 passed in 4.15s
```

Existing `_keep_typing` test coverage in `tests/gateway/test_base_topic_sessions.py`, `test_signal.py`, `test_discord_reactions.py`, `test_run_progress_topics.py` still passes (180/181; the one failure is pre-existing on main, unrelated).

## Context

Reported symptom: "it stops typing and just stops working entirely... when I say wtf are you doing, it says it was interrupted, but it was NOT doing anything." Root cause was Anthropic going dark for a few minutes → opus-4.7 first-token latency stalled past `HERMES_STREAM_READ_TIMEOUT` → model-stream retried silently → during that window the platform typing refresh was hitting the same degraded network and individual `send_chat_action` calls were taking longer than the 2s refresh cadence, killing the bubble. This PR only addresses the typing-indicator symptom; the model-side retry behavior already worked correctly and isn't changed.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_keep_typing_timeout.py`