**feat(kanban): add scheduled status for delayed follow-ups**

Salvages #24533 by @roycepersonalassistant.

Adds a first-class `scheduled` Kanban status for time-delay follow-ups that aren't waiting on human input. (Main already had `scheduled` in `VALID_STATUSES` from earlier work but lacked the surface.)

- `hermes kanban schedule <task_id> [reason]` CLI command
- Dashboard/API transitions to/from Scheduled
- `unblock_task()` now releases both `blocked` AND `scheduled` tasks (re-checking parent dependencies before moving to ready/todo)
- i18n + docs updates

Resolved 4 conflicts. Kept HEAD's failure-counter reset on unblock alongside the PR's scheduled state, kept HEAD's `running` direct-set rejection, combined both bulk-status branches. Dropped the dist/ bundle changes since they were months stale against current main (would conflict catastrophically with the bundle's recent rebuilds).

Authorship preserved via rebase merge.

## Validation
- 2 schedule tests pass.