**feat(gateway): configurable Telegram reply threading mode**

## Summary

Adds a `reply_to_mode` setting to control whether Telegram replies quote/thread to the user's original message.

- **`off`**: Never thread replies — no quote bubble shown
- **`first`**: Only the first chunk threads to the user's message (default, preserves existing behavior)
- **`all`**: All chunks in multi-part replies thread to the user's message

### Configuration

**Via gateway config YAML:**
```yaml
platforms:
  telegram:
    reply_to_mode: "off"  # or "first" (default) or "all"
```

**Via environment variable:**
```
TELEGRAM_REPLY_TO_MODE=off
```

### Changes

- `gateway/config.py` — Added `reply_to_mode` field to `PlatformConfig` with serialization and env var override
- `gateway/platforms/telegram.py` — Added `_should_thread_reply()` method, updated `send()` to use it
- `tests/gateway/test_telegram_reply_mode.py` — 25 tests covering all modes, config, serialization, and env var overrides

### Credit

Based on PR #855 by @raulvidis. Cherry-picked and adapted to current main (preserved retry logic, used explicit `@pytest.mark.asyncio` decorators instead of global `asyncio_mode` change).

All 1428 gateway tests pass.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_telegram_reply_mode.py`