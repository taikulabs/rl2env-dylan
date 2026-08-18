**fix(api_server): persist ResponseStore to SQLite across restarts**

## Summary

The `/v1/responses` endpoint used an in-memory `OrderedDict` that lost all conversation state on gateway restart. Users on platforms with hibernating VMs or frequent restarts lost multi-turn context entirely.

**Fix:** Replace the in-memory store with SQLite at `~/.hermes/response_store.db`.

### What changed
- `ResponseStore` now backed by SQLite with WAL mode
- Responses and conversation name mappings survive gateway restarts
- Same LRU eviction behavior (configurable `max_size`, default 100)
- Falls back to in-memory SQLite if disk path is unavailable
- Conversation name→response_id mapping moved into the store (was a separate dict)
- 3 tests updated to use new store API

### Why not a new endpoint
PR #2437 proposed adding a separate `/v1/message` endpoint to solve this. Making the existing endpoint persistent is simpler and avoids API surface sprawl.