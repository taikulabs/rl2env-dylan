**fix(gateway): strip cursor from frozen message on empty fallback continuation**

## Summary
A streaming message is no longer left frozen with a visible `▉` cursor when fallback mode kicks in and has nothing new to send at stream end. The cursor-stripping edit that was missing from the empty-continuation early-return path is now attempted before returning.

## Changes
- `gateway/stream_consumer.py` — in `_send_fallback_final()`, when `continuation.strip() == ""` and `final_text` doesn't differ meaningfully from the visible prefix, attempt a best-effort edit to strip the cursor before the early return. Harmless when fallback wasn't armed or the cursor isn't present; crash-proof if the edit itself fails.
- `tests/gateway/test_stream_consumer.py` — 3 regression tests in `TestCursorStrippingOnFallback`: cursor stripped on empty continuation, no edit attempted when cursor is not configured, edit-failure handled without corrupting `_last_sent_text`.

## Validation
| | Before | After |
|---|---|---|
| `tests/gateway/test_stream_consumer.py` | 64 passing | 67 passing (3 new) |
| Cursor edit attempt in `_send_fallback_final` empty-continuation path | not attempted | attempted (best-effort) |

Live-tested against the Phase 1 integration harness (real agent on OpenRouter → real `GatewayStreamConsumer` → mock adapter with simulated flood control): all three scenarios — no flood, flood@1, flood@2 — deliver content correctly without regressions. The remaining cursor residue visible in the live test is on a separate code path (`_try_strip_cursor()` inside the #8124 segment-flush helper hitting an active flood window), outside the scope of this fix.

## Closes
- #7183 — "Telegram streaming message frozen with cursor (▉) when final cursor-removal edit fails after tool call"

## Credit
- @Tranquil-Flow — PR #7429 implementation + 3 regression tests; authorship preserved on ` via `--author`. The cursor-strip logic was adapted onto current main because the surrounding `_send_fallback_final` block grew the #10807 stale-prefix handling after #7429 was submitted, so the strip lives in the new `else`-branch where we still return early instead of the original single-exit early-return.
- @austinmw — filed #7183 with the root-cause analysis and a deterministic repro that informed the test design.

## Relationship to recent streaming fixes
This is the last defense-in-depth piece for the Discord "section-header with stuck cursor" pattern:
- `d7607292` (Apr 11) — adaptive backoff + `_try_strip_cursor()` on fallback entry
- `1d1e1277` (#12414, Apr 19) — flush undelivered tail before segment reset
- `c49e848d` (this PR) — cursor strip on empty fallback continuation

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_stream_consumer.py`