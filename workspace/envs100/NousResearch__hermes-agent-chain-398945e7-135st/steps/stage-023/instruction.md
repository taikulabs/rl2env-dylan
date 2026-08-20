**fix(gateway): drain pending messages via fresh task, not recursion**

(no description was recorded for this change)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_duplicate_reply_suppression.py`
- `tests/gateway/test_pending_drain_no_recursion.py`