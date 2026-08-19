**feat(kanban): configure worktree paths and branches**

Salvages #26496 by @aqilaziz.

Adds `branch_name` column + CLI flag so tasks with `workspace_kind='worktree'` can pin a target branch on create. Schema migration is additive (additive ALTER TABLE in `_migrate_add_optional_columns`).

- `Task.branch_name` field + DB column + migration
- `create_task()` accepts `branch_name` kwarg
- `hermes kanban create --branch <name>` flag
- `kanban show` output includes `Branch:` line when set

`); the PR's tip was an unrelated service-path-dirs commit. Resolved 2 conflicts in `kanban_db.py` (INSERT column list + show output) alongside main's `session_id` and `max_runtime_seconds` additions — kept all three. Dropped an unrelated test_provider_parity formatting tweak. Authorship preserved via rebase merge.

## Validation
- 9 branch/worktree tests pass.