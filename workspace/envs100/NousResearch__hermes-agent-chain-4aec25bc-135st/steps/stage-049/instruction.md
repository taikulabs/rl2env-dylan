**fix(kanban): align worker terminal timeout with task runtime**

Salvage of #26177 from @qWaitCrypto onto current main.

When a kanban task has `max_runtime_seconds`, raise the worker subprocess's `TERMINAL_TIMEOUT` and `TERMINAL_MAX_FOREGROUND_TIMEOUT` to runtime − 30s grace. Long worker commands no longer get killed by the inherited generic terminal default (180s) before the kanban runtime cap.

- Worker-scoped only; CLI/gateway terminal settings untouched.
- Existing larger timeouts preserved.
- Uncapped tasks unchanged.
- Adds runtime/terminal timeout budget to `build_worker_context()`.

. Original PR: #26177.

## Validation
- 4 new targeted tests passing.