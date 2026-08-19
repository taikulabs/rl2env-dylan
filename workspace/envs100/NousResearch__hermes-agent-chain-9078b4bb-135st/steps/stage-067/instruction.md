**fix(compress): reserve output tokens in the compaction threshold (#23767, #43547)**

## Summary

The compaction trigger compared estimated input against `context_length × threshold`, but the provider reserves `max_tokens` of **output** out of that same window. With a large `max_tokens` (e.g. 65536 on a custom provider), the usable input budget is materially smaller than the raw window — so a session could hit a provider 400 ("context length exceeded") before compaction ever fired. The threshold is now based on the **effective input budget** `(context_length − max_tokens)`. (Mode B of #23767; .)

Salvage of #43651 by @kyssta-exe — reimplemented on the current threshold surface (see below).

## Why a fresh commit (partly-superseded)

The original PR edited an inline `int(context_length * threshold_percent)` in `update_model`/`__init__`. That code was since refactored into the static `_compute_threshold_tokens()` helper (for the small-window 85% guard, #14690), and the threshold reset now runs in `update_model` alongside the #50137 calibration reset. A cherry-pick would conflict and reintroduce the old shape, so this re-implements the one surviving design point (output-token reservation) on the current surface.

## Changes

- `agent/context_compressor.py`: `_compute_threshold_tokens()` gains an optional `max_tokens` param and subtracts it from the effective window **before** both the percentage and the `#14690` small-window 85% guard; `self.max_tokens` stored in `__init__` and reused by `update_model` (optional explicit override). `max_tokens=None` (provider default) → no reservation → full-window behavior, **byte-identical to before**.
- `agent/agent_init.py`: pass `max_tokens=agent.max_tokens` at construction.
- `tests/agent/test_context_compressor.py`: 3 tests (reservation lowers threshold; small-window floor composition; `max_tokens ≥ context_length` falls back to full window).

## Design note vs original PR

The original threaded `max_tokens` as a required `update_model` kwarg but updated only the one construction caller — the other 6 `update_model` callers would have zeroed the reservation on every switch. This version **stores** `max_tokens` and reuses it across switches (the output cap is a user setting, not model-specific), so the reservation survives `/model` switches; an explicit kwarg can still override it.

## Validation

| | Result |
|---|---|
| threshold/max_tokens/compress tests | 117 passed |
| existing threshold tests (None path) | unchanged ✓ |
| ruff (diff vs main) | clean |
| Negative check | 3 new tests fail on main without the fix ✓ |
| E2E (real imports) | 200K+65536 → threshold 67232 (not 100000); None → 100000 unchanged; switch preserves reservation; explicit override works |

Interactions verified orthogonal: #50137 (calibration reset in `update_model`) and #50136 (tool-output persistence cap, different layer).

Part of #23767 — **this is the last of the 6 failure modes**; #23767 can close once this lands.

## Credit

- @kyssta-exe — #43651 originally proposed the output-token reservation in the compaction threshold. The surrounding threshold code was refactored since (#14690 small-window guard), so this re-implements that design point on the current `_compute_threshold_tokens` helper.

.

## Infographic

_Image generation is unavailable in this environment (FAL_KEY unset, no managed-provider credits); to be attached once available._