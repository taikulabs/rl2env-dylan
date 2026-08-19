**feat(kanban): stamp originating ACP session_id on tasks**

Salvages #23208 by @awizemann.

Tracks which chat session created a kanban task so clients can render a per-session board without falling back to tenant + time-window heuristics.

- **Schema** — `tasks` gains nullable `session_id TEXT` column with index. Additive migration in `_migrate_add_optional_columns`.
- **ACP propagation** — `acp_adapter/server.py` exposes originating session id via `HERMES_SESSION_ID` with proper save/restore around the agent loop.
- **Tool** — `kanban_create` reads `HERMES_SESSION_ID` (explicit `session_id` arg can override).
- **CLI** — `hermes kanban list --session <id>` filter; JSON output exposes `session_id`.

Resolved 3 conflicts (acp_adapter previous_session_id alongside main's edit_approval_token, kanban_db migration block alongside main's model_override, create_task signature alongside main's initial_status). Authorship preserved via rebase merge.

## Validation
- 5 session_id-related tests pass.