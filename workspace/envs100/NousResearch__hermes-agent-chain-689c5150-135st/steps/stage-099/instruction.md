**fix: bound auxiliary client cache to prevent fd exhaustion in long-running gateways**

## Summary

 — `_client_cache` in `auxiliary_client.py` accumulated unbounded entries because event loop `id()` was part of the cache key. Every new worker-thread event loop created a new entry for the same provider config. In long-running gateways where threads recycle frequently, this exhausted file descriptors after days of operation.

## Root Cause

The cache key included `loop_id = id(current_loop)`. When gateway worker threads create new event loops (via `_run_async()`/`asyncio.run()`), each loop gets a unique `id()`. The cache held a reference to the old loop object, preventing GC and ensuring new loops always got different IDs. Old entries with dead loops piled up — each holding an unclosed `AsyncOpenAI` client with its httpx connection pool (KQUEUE fds, unix sockets, IPv4 fds).

## Fix

- **Remove `loop_id` from cache key** — the logical key is now `(provider, async_mode, base_url, api_key, api_mode, runtime_key)`
- **Validate loop at hit time** — on async cache hits, check that the cached loop is the *current, open* loop. If the loop changed or was closed, force-close the stale client and replace the entry in-place
- **Add `_CLIENT_CACHE_MAX_SIZE = 64` safety belt** — FIFO eviction as defense-in-depth

This bounds cache growth to **one entry per unique provider config** rather than one per (config × event-loop). Cross-loop safety is preserved: different loops still get different client instances (validated by the existing `TestCrossLoopCacheIsolation` suite).

## E2E Verification

Simulated 20 sequential worker threads with different event loops for the same provider:
- **Before:** 20 cache entries (one per loop) → unbounded growth → fd exhaustion
- **After:** 1 cache entry (replaced in-place) + 20 unique clients (cross-loop safe)

## Test Results

- 14 targeted tests pass (9 in `test_async_httpx_del_neuter.py` + 5 in `test_crossloop_client_cache.py`)
- 3 new tests: `TestClientCacheBoundedGrowth` — stale loop replacement, no-growth verification, max-size eviction
- 1885 passing in broader agent/run_agent suite (9 pre-existing failures unrelated to this change)