**fix: /browser connect CDP override takes priority over Camofox**

## Summary

When a user runs `/browser connect` to attach browser tools to their real Chrome instance via CDP, the `BROWSER_CDP_URL` env var is set. However, every browser tool function checks `_is_camofox_mode()` **first**, which short-circuits to the Camofox backend before `_get_session_info()` ever reaches the CDP override check.

**Result:** `/browser connect` confirms success but browser tools silently route to Camofox anyway.

## Fix

`is_camofox_mode()` in `tools/browser_camofox.py` now returns `False` when `BROWSER_CDP_URL` is set. This is one change in one place that covers all ~15 browser tool functions.

The logic: `/browser connect` is an explicit user override — they want their real Chrome, not Camofox. Empty/whitespace `BROWSER_CDP_URL` does not suppress Camofox (only a real value does).

## Files changed
- `tools/browser_camofox.py` — `is_camofox_mode()` checks for CDP override
- `tests/tools/test_browser_camofox.py` — 2 new tests for CDP priority behavior

## Test results
All 164 browser tests pass.

Reported by SkyLinx on Discord.