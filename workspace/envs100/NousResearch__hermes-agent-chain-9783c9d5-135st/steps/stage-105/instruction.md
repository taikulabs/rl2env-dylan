**fix: create AsyncOpenAI lazily in trajectory_compressor to avoid closed event loop**

The `AsyncOpenAI` client in `trajectory_compressor.py` was created eagerly at init. When `process_directory()` calls `asyncio.run()` (creates+closes a loop), a second call crashes with `RuntimeError: Event loop is closed` because the cached client's httpx transport is bound to the dead loop.

Same class of bug as PR #3398 (main agent's event loop fix), different code path.

**E2E verified:**
- Before fix: `AsyncOpenAI()` called 1 time at init, same stale instance reused across loops ❌
- After fix: `async_client=None` at init, `_get_async_client()` creates fresh instance per loop ✅

5 tests pass including source verification.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_trajectory_compressor_async.py`