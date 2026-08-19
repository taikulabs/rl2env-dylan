**fix(gateway): preserve _session_tasks on guard mismatch to heal stale session lock**

## Summary

 — `_session_task_is_stale()` misses a stale session lock when the task entry was already cleaned up, causing a permanent session deadlock.

In `_process_message_background`'s finally block (`gateway/platforms/base.py`), an owner task that completed would `del self._session_tasks[session_key]` **before** calling `_release_session_guard`. When a concurrent path (a reset/`new` command, or the in-band drain handoff) had swapped `_active_sessions[key]` to a different guard, `_release_session_guard` skips on the guard-mismatch check and the lock stays installed. With the task entry already deleted, `_session_task_is_stale()` then sees no owner task and reports "not stale" — so the on-entry self-heal never fires, the orphaned guard is never cleared, and the session **deadlocks permanently** (later messages received but never dispatched). Verified still live on current `main` (the finally block still deletes before releasing).

## Fix

Reorder to **release-then-conditional-delete**: release the guard first, then drop the `_session_tasks` entry **only if** the guard was actually released (`session_key` no longer in `_active_sessions`). On a guard mismatch the done-task entry survives, so the existing self-heal machinery (`_session_task_is_stale` → `_heal_stale_session_lock`) detects the stale lock and clears it on the next inbound message.

## Salvage / attribution

Cluster of 4 PRs targeted #48300; salvaged the cleanest correct approach, **#48315 (@islam666 / Elshayib)**, 

**Test hardening (co-authored):** the salvaged PR's regression test inlined a *copy* of the fixed finally-block logic, so it passed regardless of the production code (mutation-checked: the buggy `del`-first order did NOT fail it — a change-detector). The cleanup is now extracted into a callable `_cleanup_finished_session_task()` helper so the test drives the **real** production path; both the guard-mismatch (preserve) and guard-match (release+delete) branches are pinned, and the rewritten tests **fail** on the buggy order (mutation-verified).

## Tests

`tests/gateway/test_session_split_brain_11016.py` — 15 pass (incl. the rewritten guard-mismatch contract + new positive-path test). 820 pass across the broader session/guard/split-brain suite, no regressions.