**fix(gateway): bound _agent_cache with LRU cap + idle TTL eviction**

## What this PR does (zoomed out)

The gateway caches one `AIAgent` per session_key so consecutive messages in the same chat reuse the frozen system prompt (required for prompt-caching to hit). That cache had no size limit and no idle eviction — entries were only dropped on explicit `/new`, `/model`, or session reset.

In a long-lived gateway serving many Telegram/Discord/etc. chats, this meant cached `AIAgent` objects (each holding LLM clients, tool schemas, memory providers, conversation buffers) accumulated indefinitely.

## The fix

- Cache is now an `OrderedDict` so we can pop the least-recently-used entry in O(1).
- `_enforce_agent_cache_cap()` pops entries past `_AGENT_CACHE_MAX_SIZE=64` on every insert.
- LRU order is refreshed via `move_to_end()` on cache hits.
- `_sweep_idle_cached_agents()` evicts entries whose `AIAgent._last_activity_ts` exceeds `_AGENT_CACHE_IDLE_TTL_SECS=3600`. Runs from the existing `_session_expiry_watcher` — no new background task.
- The expiry watcher now also pops the cache entry after calling `_cleanup_agent_resources` on a flushed session. Previously the agent was shut down but its reference stayed in the cache dict, so it could never be GC'd.
- Evicted agents have `_cleanup_agent_resources()` called on a daemon thread so the cache lock isn't held during slow teardown (memory provider shutdown, httpx close, etc.).

Both tuning constants live at module scope (`_AGENT_CACHE_MAX_SIZE`, `_AGENT_CACHE_IDLE_TTL_SECS`) so tests can monkeypatch them easily.