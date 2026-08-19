**fix(tools): enforce ID uniqueness in TODO store during replace operations**

## Summary

Salvage of #7829 by @WAXLYY.

Deduplicates todo items by ID before writing to the store, keeping the last occurrence. Prevents ghost entries when the model sends duplicate IDs in a single `write()` call, which corrupts subsequent merge operations.

## Changes

- `tools/todo_tool.py`: Add `_dedupe_by_id()` static method, applied in both replace and merge write paths
- `tests/tools/test_todo_tool.py`: Regression test for duplicate ID deduplication

## Follow-up simplification

Simplified the contributor's `_dedupe_by_id` implementation — replaced the null-slot elimination approach with a simpler last-index dict + sorted reconstruction. Same behavior, half the code. Also removed redundant ID pre-normalization (already handled by `_validate()`).

## Tests

```
12 passed in 0.05s
```