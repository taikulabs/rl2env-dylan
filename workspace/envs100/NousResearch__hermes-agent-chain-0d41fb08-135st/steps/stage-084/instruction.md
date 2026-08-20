**fix(feishu) + feat(matrix): group chat events + DM mention threads**

## Summary
Two platform adapter fixes salvaged from #6975 and #6957.

### 1. fix(feishu): register group chat member event handlers (#6975, @ygd58)
`_on_bot_added_to_chat` and `_on_bot_removed_from_chat` existed but weren't registered in `_build_event_handler()` — group chat bot events were silently dropped. 2-line fix.

### 2. feat(matrix): MATRIX_DM_MENTION_THREADS env var (#6957, @fxfitz)
When enabled, @mentioning the bot in a DM creates a thread. Default false. Config bridge (matrix.dm_mention_threads), 6 tests, docs updated in env var reference and Matrix user guide.

## Test results
- 36 matrix mention tests passing (30 existing + 6 new)
- feishu.py and matrix.py compile clean

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_matrix_mention.py`