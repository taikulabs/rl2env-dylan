**feat(discord): add message processing reactions (salvage #1980)**

Salvage of #1980 by @alanwilhelm. Cherry-picked discord.py cleanly; base.py had conflicts from 602 commits of drift — resolved by implementing the hooks fresh on current main.

## Feature

Discord messages now get emoji reactions showing processing status:
- 👀 when Hermes starts processing
- ✅ on successful completion (delivery confirmed)
- ❌ on failure, error, or cancellation

## Architecture

Lifecycle hooks in the base adapter make this extensible to other platforms:
- `on_processing_start(event)` — called before handler runs
- `on_processing_complete(event, success)` — called after delivery (or on error/cancel)
- `_run_processing_hook()` — error-isolated wrapper so hook failures never break message flow

Delivery tracking via closure (`_record_delivery`) accurately determines success based on whether the send actually worked, not just whether a response was generated.

## Tests

1768 gateway tests passed + 3 new Discord reaction tests + base hook lifecycle tests. 0 regressions.