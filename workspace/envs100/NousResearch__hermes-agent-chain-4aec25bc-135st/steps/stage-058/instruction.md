**fix(kanban): detect cycles in decompose_triage_task sibling-link pre-validation**

Salvage of #28050 by @EloquentBrush0x onto current main.

## Summary
`decompose_triage_task` inlines INSERTs for atomicity and skipped the cycle check that `link_tasks()` does per-edge via `_would_cycle()`. A cyclic sibling parent graph (e.g. `A.parents=[1]`, `B.parents=[0]`) succeeded silently and deadlocked every involved child in `todo` forever — `recompute_ready()` can never promote them.

## Changes
- `hermes_cli/kanban_db.py`: Kahn topological sort over the sibling parent-index list in the pre-validation block, before any DB writes. O(N+E), no new imports.
- `tests/hermes_cli/test_kanban_decompose_db.py`: new `test_decompose_rejects_cyclic_parents`.

## Validation
- 8/8 `test_kanban_decompose_db` tests pass (7 pre-existing + 1 new).

.