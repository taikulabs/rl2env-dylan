**fix(tools): isolate get_tool_definitions quiet_mode cache + dedup LCM injection**

Salvages #17337 by @Sanjays2402 onto current `main`. .

Long-lived Gateway processes were sending duplicate tool names to providers that enforce uniqueness (DeepSeek, Xiaomi MiMo, Moonshot/Kimi → HTTP 400). TUI was unaffected because it runs with `quiet_mode=False` and skips the cache.

## Root cause (two layered bugs)

1. `model_tools.get_tool_definitions(quiet_mode=True)` aliased its cached list on the first uncached call. The cache-hit path already returned `list(cached)`, but the first call stored and returned the same object. `run_agent` then mutates `self.tools` in place, so agent init #1 poisoned the cache and every subsequent init re-appended LCM schemas.
2. `run_agent.py` LCM context-engine injection had no dedup, unlike the memory-tools injection right above it.

## Fix (defense in depth)

- `model_tools.py` — cache the result then return `list(result)` on the uncached branch, mirroring the cache-hit path
- `run_agent.py` — build `_existing_tool_names` from `self.tools` and skip already-present schemas, mirroring memory-tools dedup

## Validation

```
scripts/run_tests.sh tests/test_get_tool_definitions_cache_isolation.py tests/test_model_tools.py
29 passed in 3.98s
```

5 new regression tests pin the behavior; 23 existing `test_model_tools.py` tests still pass. Authorship preserved for @Sanjays2402.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_get_tool_definitions_cache_isolation.py`