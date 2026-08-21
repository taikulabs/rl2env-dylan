**fix(approval): wake blocked gateway approvals on session cleanup**

Salvages #18044 onto current main. Authorship preserved via cherry-pick.

## Summary
Gateway approval waiters blocked in `threading.Event.wait()` now get signalled (and marked as denied) when `clear_session()` runs during `/new`, `/resume`, or `/branch` — instead of idling until the dangerous-command approval timeout expires.

## Changes
- `tools/approval.py`: `clear_session()` now pops gateway queues, sets `entry.result="deny"`, and calls `entry.event.set()` outside the lock. Same lock-scope fix applied to sibling `unregister_gateway_notify()` (prevents deadlock when waiter re-acquires `_lock`).
- 2 regression tests in `tests/gateway/`.

## Validation
- `scripts/run_tests.sh tests/gateway/test_approve_deny_commands.py tests/gateway/test_session_boundary_security_state.py` → 25/25 passing (3 runs).

Credit: @Yukipukii1 (original PR #18044)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_approve_deny_commands.py`
- `tests/gateway/test_session_boundary_security_state.py`