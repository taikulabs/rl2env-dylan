**fix(cli): make /new, /reset, and /clear start real fresh sessions**

## Summary
- make `/new`, `/reset`, and `/clear` create a real fresh CLI session instead of only clearing in-memory history
- create a new SessionDB row when starting fresh, reset the agent DB flush cursor/todo state, and refresh session timing/bookkeeping
- update command descriptions and add regression coverage for `/new`, `/reset`, and `/clear`

## Why
PR #899 identified the right UX problem, but on current main the implementation was stale and incomplete: switching `session_id` without creating a new DB session row breaks follow-up logging, and agent per-session state also needed to be reset.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_cli_new_session.py`