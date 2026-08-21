**feat: auto-reconnect failed gateway platforms with exponential backoff**

## Summary

When a messaging platform fails to connect at startup (e.g. transient DNS failure, network timeout) or disconnects at runtime with a retryable error, the gateway now queues it for background reconnection instead of giving up permanently.

**Problem:** A DNS blip during gateway startup caused Telegram and Discord to be permanently unavailable until manual restart. The gateway had no retry mechanism for failed platform connections.

## Changes

◆ **`gateway/run.py`** — Core reconnection logic:
  - Added `_failed_platforms` tracking dict to `GatewayRunner.__init__`
  - Startup connection loop now queues failed platforms for retry (retryable errors only)
  - New `_platform_reconnect_watcher()` background task with exponential backoff (30s → 60s → 120s → 240s → 300s cap, max 20 attempts)
  - `_handle_adapter_fatal_error()` now queues retryable runtime disconnections for reconnection instead of triggering gateway shutdown
  - On successful reconnect: adapter is wired up, delivery router updated, channel directory rebuilt

◆ **`tests/gateway/test_platform_reconnect.py`** — 13 new tests covering:
  - Startup failure queueing
  - Reconnect success/failure/backoff/max-attempts/idle behavior
  - Non-retryable error removal from queue
  - Runtime disconnection queueing and shutdown prevention

◆ **`tests/gateway/test_runner_fatal_adapter.py`** — Updated existing test to reflect new behavior (retryable errors now queue for reconnection instead of shutting down)

## Design

- Backoff: `min(30 * 2^(attempt-1), 300)` seconds between retries
- Max 20 attempts (~100 min at cap) before giving up
- Non-retryable errors (bad token, auth failure) are never retried
- Watcher checks every 10 seconds for platforms due for retry
- When all adapters disconnect but platforms are queued, gateway stays alive
- Watcher runs even when no platforms initially failed (handles runtime disconnections)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_platform_reconnect.py`
- `tests/gateway/test_runner_fatal_adapter.py`