**fix(discord): decouple readiness from slash sync**

## Summary

Salvage of #7979 by @helix4u onto current main. .

Three fixes for Discord gateway appearing healthy while not actually connected:

1. **Decouple Discord readiness from slash sync** — `_ready_event.set()` now fires after connection + allowlist resolution, before slash command sync. Sync runs in a background task with 30s timeout. Bot can process messages immediately instead of waiting for potentially slow `tree.sync()`.

2. **Fix `write_runtime_status()` sentinel** — Uses `_UNSET` sentinel so passing `error_code=None` explicitly clears stale fields. Previously, `None` was indistinguishable from "not passed" due to `if X is not None:` guards. This fixes existing broken clearing calls in `_mark_connected()` and startup.

3. **Per-platform state tracking** — Adds `_update_platform_runtime_status()` in the gateway runner to write granular platform states (`connecting`, `connected`, `retrying`, `fatal`) during startup, reconnect, and error handling. Makes `gateway_state.json` actually useful for diagnostics.

## Test results

- 21 targeted tests pass (discord connect, status, runner startup)
- 2560 gateway tests pass (25 pre-existing failures unrelated to this PR)
- E2E verified: sentinel correctly clears stale fields while leaving untouched fields unchanged

Cherry-picked with original authorship preserved.