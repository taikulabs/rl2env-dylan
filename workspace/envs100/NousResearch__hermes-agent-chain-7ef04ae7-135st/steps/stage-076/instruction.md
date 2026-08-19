**fix(auxiliary): stop SDK retries from multiplying compression stall**

## Summary

A slow auxiliary compression endpoint no longer stalls a send for many minutes. The aux OpenAI clients were built without overriding the SDK's default `max_retries=2`, so every auxiliary call silently made up to 3 attempts against a slow/hung endpoint — a 120s timeout could block ~360s before Hermes saw a single failure. On the critical compression preflight path, Hermes then layered its own same-provider timeout retry on top, roughly doubling the user-visible stall again before fallback (issue #54465).

This is the retry-multiplication root cause. The resume-wedge / cooldown-persistence half landed separately in #55499.

## Changes

- `agent/auxiliary_client.py`: build both the sync (`_create_openai_client`) and async (`_to_async_client`) aux clients with `max_retries=0` (via `setdefault`, so an explicit caller override still wins). Hermes already owns retry + provider/model fallback policy.
- `agent/auxiliary_client.py`: for `task == "compression"`, skip the same-provider transient retry on a full-budget **timeout** and fall straight through to the fallback chain. Fast blips (streaming-close, 5xx) still retry, since those are cheap.
- `agent/auxiliary_client.py`: add `_is_timeout_error` to distinguish a full-budget timeout from a fast connection drop.

## Validation

| Scenario | Before | After |
|---|---|---|
| Aux call against a slow endpoint (120s timeout) | SDK retries internally → ~360s before Hermes sees one failure | 1 attempt, fails at ~120s |
| Compression times out on the critical path | same-provider retry → another full timeout before fallback (~720s total) | skips retry, falls straight to fallback |
| Compression hits a fast streaming-close | retries same provider | unchanged — still retries |
| Non-compression aux task times out | retries same provider once | unchanged — still retries |
| Explicit `max_retries=N` caller override | honored | honored |

- 262 targeted tests pass: `tests/agent/test_auxiliary_client.py` (253 existing + 9 new).
- `tests/agent/test_context_compressor.py`, `tests/agent/test_turn_context.py` pass.
- E2E with the real OpenAI SDK: `_create_openai_client(...).max_retries == 0`, explicit override honored, real `APITimeoutError` classified as timeout while a streaming-close is not.

## Infographic

![Compression stall capped](https://v3b.fal.media/files/b/0aa05a86/9zgtZ4GzPBAgjp5iaPYxO_IPXkDGn7.png)

Addresses #54465.