**feat(kanban): filter tasks by workflow fields**

Salvages #26745 by @nehaaprasaad.

Exposes filtering for the existing `workflow_template_id` and `current_step_key` columns on `Task`:
- `list_tasks()` accepts `workflow_template_id` and `current_step_key` kwargs
- `hermes kanban list` adds matching CLI flags
- Dashboard plugin_api exposes the filters

Resolved a small conflict in `list_tasks` signature alongside main's `session_id` and `order_by` additions; combined all three into the single filter list. Authorship preserved via rebase merge.