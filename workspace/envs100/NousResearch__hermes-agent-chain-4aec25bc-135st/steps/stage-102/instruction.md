**fix(kanban): reject direct running transitions in dashboard bulk updates**

Salvages #24050 by @kronexoi.

Single-task PATCH already rejects `status='running'` (bypasses dispatcher/claim invariant), but bulk-update endpoint still accepted it. Aligns bulk with single by emitting an error result for any 'running' entry.

Original branch was stale; applied the substantive fix manually onto current main. Authorship preserved via rebase merge.

## Validation
- New test (test_bulk_status_running_rejected) passes.