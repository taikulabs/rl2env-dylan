**fix(gateway): flush undelivered tail before segment reset**

## Summary
Text generated between a mid-stream edit failure and a tool boundary is no longer silently dropped. Root cause: `_reset_segment_state()` on a tool boundary wiped `_accumulated` even when the most recent edit had failed, discarding un-delivered content.

The fix flushes the undelivered tail as a continuation message before the segment reset, computed relative to the last successfully-delivered prefix so it doesn't duplicate what the user already saw. Best-effort cursor strip on the partial message is also attempted when fallback mode hasn't already done so.

## Changes
- `gateway/stream_consumer.py` — new `_flush_segment_tail_on_edit_failure()` helper called before `_reset_segment_state()` on segment breaks, guarded on `_accumulated and not current_update_visible and _message_id and _message_id != "__no_edit__"`.
- `tests/gateway/test_stream_consumer.py` — new `test_segment_break_after_mid_stream_edit_failure_preserves_tail` (matches austinmw's repro script verbatim) + updated existing `test_segment_break_clears_failed_edit_fallback_state` which had inadvertently codified the drop-the-tail behavior.

## Validation
| | Before | After |
|---|---|---|
| `tests/gateway/test_stream_consumer.py` | 63 passing | 64 passing (1 new) |
| austinmw's #8124 repro | `User received: 'Hello world ▉ Here is the tool result.'` (" more" dropped) | `User received: 'Hello world ▉ more Here is the tool result.'` (all text delivered) |

## Closes
- #8124 — "Streaming text silently dropped when tool boundary arrives during fallback mode"

## Credit
- @konsisumer — PR #11974 implementation + austinmw's repro as a regression test; authorship preserved on ` via cherry-pick.
- @lawrence3699 — PR #8417 identified the same bug first (Apr 12, 6 days before #11974). The simpler 3-line approach there piggybacks on `_fallback_final_send=True`, which only latches after `_MAX_FLOOD_STRIKES=3` consecutive failures — in the actual bug scenario fallback isn't yet armed when the tool boundary arrives, so that approach doesn't fully cover the bug. #11974's condition (`_accumulated AND not current_update_visible`) fires on any unsuccessful segment-break edit and handles the common pre-fallback case.
- @austinmw — filed #8124 with the deterministic repro script this fix uses as its regression test.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_stream_consumer.py`