**fix(weixin): add per-chunk retry with backoff for text delivery**

## Summary

When sending multi-chunk Weixin responses, individual chunks can fail due to transient iLink API errors. Previously a single failure aborted the entire message. Now each chunk retries with linear backoff before giving up, and the same `client_id` is reused across retries for server-side deduplication.

### What changed

- **`_send_text_chunk()`** — new retry wrapper around `_send_message()` with configurable attempts and backoff
- **Configurable pacing** — replaces the hardcoded 0.3s delay from #7903 with `send_chunk_delay_seconds` (default 0.35s)
- **Config/env vars**: `send_chunk_delay_seconds`, `send_chunk_retries` (default 2), `send_chunk_retry_delay_seconds` (default 1.0s)
- **Tests** — inter-chunk delay test + flaky-send retry test with client_id dedup verification

### Files changed (+105/-8)
- `gateway/platforms/weixin.py` — config properties, `_send_text_chunk()` retry wrapper, updated `send()`
- `tests/gateway/test_weixin.py` — 2 new tests (TestWeixinChunkDelivery)

### Test results
20/20 weixin tests pass

Salvaged from PR #7899 by @corazzione. Contributor authorship preserved. .