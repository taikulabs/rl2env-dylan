**feat(kanban): archive --rm to hard-delete archived tasks**

Salvages #19964 by @Beandon13.

Adds `hermes kanban archive --rm` to permanently delete already-archived task ids from the board, with cascading cleanup of `task_links`, `task_comments`, `task_events`, `task_runs`, and `kanban_notify_subs`.

Safety guard: only archived tasks can be deleted. Active / blocked / done tasks must be explicitly archived first so accidental data loss requires a second deliberate action.

Original PR was severely stale against main (kanban subsystem had a month of churn). Substance applied manually onto current main, contributor authorship preserved.

## Validation
- 3 new tests pass (test_kanban_db.py + test_kanban_core_functionality.py)