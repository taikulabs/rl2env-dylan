**fix(codex): scope kanban worker writable root in app-server sandbox (salvage #26212)**

## Summary
Salvage of #26212 — codex-runtime Kanban workers (spawned via `codex app-server` with `HERMES_KANBAN_TASK` set) need to write board state (handoff/status/SQLite) to a path outside their per-task workspace. Without an explicit writable-root override, they finish the actual work and then crash/block when the kanban_complete / kanban_block tools try to write the board DB.

Fix keeps the Codex sandbox on (does NOT fall back to `danger-full-access`); just adds the Kanban root as the single extra writable root and disables network there.

## Changes
- `agent/transports/codex_app_server.py` — when `HERMES_KANBAN_TASK` is set, derive the kanban root from `HERMES_KANBAN_DB`'s parent (fallback: `HERMES_KANBAN_ROOT` or `$HERMES_HOME/kanban`) and pass three `-c` overrides: `sandbox_mode="workspace-write"`, `sandbox_workspace_write.writable_roots=[<kanban_root>]`, `sandbox_workspace_write.network_access=false`.
- `tests/agent/transports/test_codex_app_server_runtime.py` — regression test asserts (a) the kanban root is added, (b) network access is disabled, (c) no `danger-*` mode is used.
- `website/docs/user-guide/features/codex-app-server-runtime.md` — minor docs touch.

## Validation
- `scripts/run_tests.sh tests/agent/transports/test_codex_app_server_runtime.py -q` → 27/27 pass.

Original PR: #26212 — credit preserved via rebase-merge.