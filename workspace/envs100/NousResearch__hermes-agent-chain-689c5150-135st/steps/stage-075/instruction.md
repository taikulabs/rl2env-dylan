**fix(gateway): regression causing display.streaming to override root gateway streaming config**

## Summary

Salvage of PR #8347 by @asheriif — cherry-picked onto current main.

Fixes a regression introduced by PR #8006 (per-platform display config) where the CLI-only `display.streaming` config key leaks into gateway streaming decisions, causing streaming to be enabled on messaging platforms even when `streaming.enabled: false` is set.

The fix adds a guard in `resolve_display_setting()` to skip `display.streaming` at step 2 (global display settings), since that key only controls CLI terminal streaming. Gateway streaming is governed by the top-level `streaming` config, with per-platform overrides via `display.platforms.<platform>.streaming` still working.

## Changes
- `gateway/display_config.py` — skip `display.streaming` in global display resolution (step 2)
- `tests/gateway/test_display_config.py` — test that global `display.streaming` is ignored for gateway
- `tests/gateway/test_run_progress_topics.py` — integration test: `display.streaming: true` + `streaming.enabled: false` does NOT enable gateway streaming

## Test results
- 101 targeted tests passed (display_config + run_progress_topics + stream_consumer)
- 2799/2799 gateway tests passed (7 pre-existing failures in unrelated areas)

Credit: @asheriif (original implementation)