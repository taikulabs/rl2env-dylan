**fix(agent): defer preflight compaction until real usage after a compaction (#23767, #36718)**

## Summary

After a compaction, preflight could fire a **second** compaction before the provider ever reported real token usage for the now-shorter conversation. `should_defer_preflight_to_real_usage()` — the gate the preflight path consults — short-circuited to `False` on the **stale** `last_real_prompt_tokens` (the pre-compaction value, above threshold), so deferral never engaged. This adds the missing guard: defer while `awaiting_real_usage_after_compression` is set (exactly one turn, until real usage arrives). (Mode F of #23767; hardens #36718.)

## Relationship to #40582 (already merged)

#36718 was closed by #40582, which fixed a **different mechanism** for the same symptom — it stopped `turn_context.py` from clobbering the `last_prompt_tokens = -1` sentinel. That's necessary but **not sufficient**: the preflight gate is `should_defer_preflight_to_real_usage()`, which reads `last_real_prompt_tokens` (a *different* field, still stale-high post-compaction). With only #40582, `should_defer` still returns `False` and `should_compress(rough_estimate)` fires a second compaction. This PR closes that residual gate. Verified: the new regression test **fails on current main** () and passes with this fix.

## Changes

- `agent/context_compressor.py`: early-return `True` from `should_defer_preflight_to_real_usage()` when `awaiting_real_usage_after_compression` is set, placed after the `rough < threshold` cheap-exit (so below-threshold turns never over-defer).
- `tests/agent/test_context_compressor.py`: 2 tests in `TestPreflightDeferral` (defers on stale-real post-compaction; resumes normal logic once the flag clears).

## Validation

| | Result |
|---|---|
| `TestPreflightDeferral` (+2) | 5 passed |
| compressor defer/compress/update_model subset | 114 passed |
| ruff (diff vs main) | clean |
| Negative check | new test fails on main without the fix ✓ |
| E2E (real imports) | defers exactly one turn post-compaction; `update_from_response` clears the flag; below-threshold not over-deferred |

Interaction with #50137 (resets the flag on model switch): orthogonal — a switch deliberately recalibrates, so post-switch the guard correctly doesn't fire on stale post-compaction state.

Part of #23767 (does not close it — mode B still pending).

## Credit

- @ashishpatel26 — #38133 diagnosed the stale-`last_real_prompt_tokens` short-circuit and designed the `should_defer` early-return this implements.
- @Tranquil-Flow — #36769 proposed the same #36718 guard with identical placement.

Both PRs' branches also carried the flag-setting half (now on main via #40582's path) plus stale summary-prompt reverts, so this is a fresh commit of just the still-missing gate, credited above.

.

## Infographic

_Image generation is unavailable in this environment (FAL_KEY unset, no managed-provider credits); to be attached once available._

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_context_compressor.py`