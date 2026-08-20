**fix(gateway): avoid stale interrupted turn auto-continue (salvage of #16802)**

Salvage of PR #16802 by @BeliefanX, onto current main.

## Summary
Both gateway auto-continue branches (`resume_pending` and tool-tail) now gate on one signal: the age of the last raw transcript row, read BEFORE the `agent_history` build strips the `timestamp` field. Default window 1 hour, configurable via `config.yaml` `agent.gateway_auto_continue_freshness`.

**Why the original #16802 needed follow-up:** the tool-tail gate read `agent_history[-1].get("timestamp")`, but `gateway/run.py` strips `timestamp` off all tool/tool_call rows when building `agent_history`:
```python
clean_msg = {k: v for k, v in msg.items() if k != "timestamp"}
```
So at runtime that half of the fix was a silent no-op — it always returned legacy-fresh. The test for it passed only because the test harness manually injected the stripped field.

## Changes
- `gateway/run.py`:
  - New `_last_transcript_timestamp(history)` helper reads from the raw transcript BEFORE the strip
  - Both `_is_resume_pending` and `_has_fresh_tool_tail` branches now share one freshness bool
  - `_coerce_gateway_timestamp` explicitly rejects `bool` (int subclass would otherwise coerce to 0.0/1.0)
  - `_auto_continue_freshness_window()` reads `HERMES_AUTO_CONTINUE_FRESHNESS` env var (bridged from config.yaml at startup, same pattern as `HERMES_AGENT_TIMEOUT`); 0 disables the gate
  - Default window raised 15 min → 1 hour (15 min was shorter than default `gateway_timeout` of 30 min)
- `hermes_cli/config.py`: added `agent.gateway_auto_continue_freshness: 3600` to `DEFAULT_CONFIG`
- `scripts/release.py`: added BeliefanX to `AUTHOR_MAP`
- `tests/gateway/test_restart_resume_pending.py`: rewrote helper to exercise the real `history → agent_history` strip path. Added regression guard `test_stale_tool_tail_with_production_data_shape` that asserts `agent_history[-1]` carries NO `timestamp` — protects the fix against someone re-adding the stripped field. Added `TestFreshnessHelpers` (16 tests) for the helpers, env var bridge, legacy compat, and zero-window opt-out.

## Validation
| | Before | After |
|---|---|---|
| Tool-tail freshness gate at runtime | always True (dead) | reads real transcript timestamp |
| Resume-pending freshness gate | works | works (same helper) |
| Targeted suite | 60 passed | 60 passed (17 new tests) |
| E2E: config.yaml → env var → helper | — | verified 7200 flows end-to-end |
| Default window vs `gateway_timeout` (1800s) | 900s (can misclassify legit long turns) | 3600s |

.
Co-authored-by: BeliefanX <beliefanx@gmail.com>

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_restart_resume_pending.py`