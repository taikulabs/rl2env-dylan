**fix(session): clear compressor summary and turn counter on /clear and /new**

`reset_session_state()` was missing two fields added after it was written:

- `_user_turn_count`: kept accumulating across `/clear`/`/new`, affecting `flush_min_turns` guard behavior
- `context_compressor._previous_summary`: old session's compression summary leaked into new session's iterative compression

Includes 4 tests covering both fields individually, together, and the no-compressor edge case.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_session_reset_fix.py`