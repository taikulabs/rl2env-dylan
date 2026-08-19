**fix(kanban): share board, workspaces, and worker logs across profiles**

## Summary

Profile workers (`hermes -p <name>`) now share the same kanban board, workspaces, and worker-log directory as the dispatcher that spawned them — .

Root cause: `kanban_db_path()`, `workspaces_root()`, and the three worker-log-dir sites in `hermes_cli/kanban_db.py` all resolved paths through `get_hermes_home()`, which returns the **active profile's** HERMES_HOME. When the dispatcher spawned a worker with `hermes -p <profile> chat -q "work kanban task <id>"`, the worker's `_apply_profile_override()` rewrote HERMES_HOME to `~/.hermes/profiles/<profile>` and opened a profile-local `kanban.db` that didn't contain the dispatcher's task.

## Changes

**`hermes_cli/kanban_db.py`:**
- New `kanban_home()` helper resolves through `HERMES_KANBAN_HOME` → `get_default_hermes_root()`. `get_default_hermes_root()` already handles both `<root>/profiles/<name>` layouts and Docker / custom HERMES_HOME paths correctly.
- `kanban_db_path()` honours `HERMES_KANBAN_DB` first, then `kanban_home()/kanban.db`.
- `workspaces_root()` honours `HERMES_KANBAN_WORKSPACES_ROOT` first, then `kanban_home()/kanban/workspaces`.
- `_default_spawn` log dir, `gc_worker_logs`, and `worker_log_path()` all route through `kanban_home()` — these three sibling sites were the log-dir tail end of the same bug.
- `_default_spawn()` now injects `HERMES_KANBAN_DB` and `HERMES_KANBAN_WORKSPACES_ROOT` into the worker subprocess env. Defense-in-depth: even when the worker's `get_default_hermes_root()` resolution disagrees with the dispatcher's (unusual symlink / Docker layouts), the two processes still open the same SQLite file.
- All three env overrides use `.expanduser()` for consistency.

**`hermes_cli/kanban.py`:** help string for `log` subcommand updated (`$HERMES_HOME/kanban/logs/` → `<kanban-root>/kanban/logs/`).

**`tests/hermes_cli/test_kanban_db.py`:** 12 regression tests under `TestSharedBoardPaths` covering default install, profile-worker convergence, Docker custom root, Docker profile layout, `HERMES_KANBAN_HOME` override, per-path `HERMES_KANBAN_DB` and `HERMES_KANBAN_WORKSPACES_ROOT` pins, empty/whitespace overrides falling through, real SQLite cross-profile handoff, and dispatcher env-injection on spawn.

**`website/docs/reference/environment-variables.md`:** documents the three new kanban env vars.

## Validation

| | Before | After |
|---|---|---|
| `hermes -p worker` worker opens | `~/.hermes/profiles/worker/kanban.db` | `~/.hermes/kanban.db` |
| `hermes kanban tail <id>` from profile | silent (empty file in profile dir) | reads dispatcher's log |
| Docker `/opt/hermes/profiles/x` worker | `/opt/hermes/profiles/x/kanban.db` | `/opt/hermes/kanban.db` |
| Kanban targeted tests | n/a | `221 passed` (`test_kanban_db` + `test_kanban_cli` + `test_kanban_core_functionality` + `test_kanban_tools`) |
| E2E (real imports, real SQLite) | n/a | 5/5 scenarios pass: dispatcher/worker converge, `HERMES_KANBAN_DB` pin wins, cross-profile SQLite handoff, dispatcher env injection |

## Consolidation

This PR fuses the best aspects of the seven parallel PRs that targeted #18442:

- **Base commit** (@GodsBoy, #19350): `kanban_home()` helper anchored at `get_default_hermes_root()`, reroutes **all 5 kanban path sites** through it (the 3 sibling log-dir sites were missed by every other PR), 8-test regression class including a real-sqlite dispatcher/worker convergence test.
- **Per-path env overrides** (from @cg2aigc, #19100): `HERMES_KANBAN_DB` and `HERMES_KANBAN_WORKSPACES_ROOT` pins with highest precedence.
- **Dispatcher env injection** (from @quocanh261997 #18300, @cg2aigc #19100): worker subprocess gets both pins injected so symmetric resolution is guaranteed even under unusual symlinks / Docker layouts.
- **`get_default_hermes_root()` direction** first proposed by @beibi9966 and @Gosuj.

, #18503, #18670, #18985, #19037, #19056, #19100. , .