**fix(security): redact secrets in background process + foreground env-dump output**

## Summary
Background-process stdout and foreground env-dump output are now redacted on every terminal surface — closing the `redact_secrets` gaps in #43025.

Root cause: terminal-output redaction was incomplete. The foreground `terminal` path redacted with a hardcoded `code_file=True` (which skips the `KEY=VALUE` pass), and the background `process` path + the gateway background-process watcher had **no redaction at all** — so a `printenv`/server/test emitting a key leaked verbatim to the model, `session.db`, and the CLI/messaging display.

## Changes
- `agent/redact.py`: new `is_env_dump_command()` + `redact_terminal_output(output, command)` — a single policy for all terminal-output surfaces. Env-dump commands (`env`/`printenv`/`set`/`export`/`declare`) run the ENV-assignment pass (`code_file=False`) so opaque tokens with no vendor prefix are masked; every other command stays on `code_file=True` to avoid false positives on source/config dumps.
- `tools/process_registry.py`: `_handle_process` routes `poll`/`log`/`wait` output through the redactor (Gap 1). Added `command` to the `read_log`/`wait` result dicts so env-dump detection works there too.
- `tools/terminal_tool.py`: foreground path now uses `redact_terminal_output(output, command)` so env dumps get the `KEY=VALUE` pass (Gap 2).
- `gateway/run.py`: background-process watcher completion/progress notifications are redacted before delivery.
- Respects `security.redact_secrets` (no `force`) — the documented opt-out is preserved.

## Validation
| Surface | Before | After |
|---|---|---|
| `process(poll/log/wait)` of `printenv` | raw key to model/db/display | masked (opaque + prefix) |
| Gateway bg-process watcher message | raw output buffer | masked |
| Foreground `printenv` opaque token | leaked (code_file skipped ENV pass) | masked |
| Foreground `cat config.py` (`MAX_TOKENS=100`) | preserved | preserved (no false positive) |
| `security.redact_secrets: false` | n/a | raw passthrough (opt-out honored) |

E2E: live `printenv` background process spawned via `spawn_local`, confirmed `poll`/`log`/`wait` all mask opaque + `sk-` keys; disabled-toggle confirmed raw. Targeted suites: 232 passed (`test_redact`, `test_process_registry`, `test_notify_on_complete`, `test_redact_config_bridge`), 13 new regression tests.

## Infographic
![Terminal-output redaction](https://v3b.fal.media/files/b/0aa0179c/WKGwYPORThNyNPJMzU-kA_68vjrtwA.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_redact.py`
- `tests/tools/test_process_registry.py`