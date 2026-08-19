**fix: reopen resumed gateway sessions in sqlite**

## Summary

Salvage of #8914 by @gaixianggeng onto current main.

When the gateway's `/resume` switches to a previously-ended session via `switch_session()`, the old session is correctly ended in SQLite but the target session's `ended_at`/`end_reason` are never cleared. The CLI already calls `reopen_session()` (cli.py:4202), so this is a parity gap.

Fix: call `self._db.reopen_session(target_session_id)` in `SessionStore.switch_session()` after ending the old session, using the same try/except pattern.

## Changes
- `gateway/session.py`: add `reopen_session()` call in `switch_session()`
- `tests/gateway/test_session.py`: regression test for resumed session state

## Validation
- 61/61 gateway session tests pass
- E2E tested with real `SessionDB` against isolated HERMES_HOME
- Live tested against a copy of production state.db — correct schema, real ended sessions reopened successfully
- Edge cases verified: already-active target, same-session no-op, nonexistent DB target