**feat(gateway): add ignored_threads config for Telegram**

## Summary

Adds `ignored_threads` config for Telegram so bots can silently ignore specific forum topics in supergroups before any message processing happens. Messages from ignored thread IDs are dropped in `_should_process_message()` before any agent work — zero LLM cost, zero noise.

Salvaged from #9348 by @Jiawen-lee (cherry-picked onto current main with original authorship preserved).

## Changes

- `gateway/platforms/telegram.py` — `_telegram_ignored_threads()` helper + early-return check in `_should_process_message()`
- `gateway/config.py` — bridges top-level `telegram.ignored_threads` to `TELEGRAM_IGNORED_THREADS` env var
- `tests/gateway/test_telegram_group_gating.py` — tests for feature + config bridging

## Config

```yaml
platforms:
  telegram:
    extra:
      ignored_threads:
        - 31
        - 42
```

Or top-level:
```yaml
telegram:
  ignored_threads:
    - 31
    - 42
```

## Test results

```
tests/gateway/test_telegram_group_gating.py: 8 passed
tests/gateway/: 2827 passed, 16 failed (pre-existing, unrelated)
```