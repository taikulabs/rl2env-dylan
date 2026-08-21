**fix(gateway): scope /yolo to the active session**

## Summary
Salvage of PR #7031 by @tesseract2026, cherry-picked onto current main.

Gateway `/yolo` was flipping the process-global `HERMES_YOLO_MODE` env var. In a multi-chat gateway, turning YOLO on in one chat silently bypassed dangerous-command approvals for every other active session.

## Changes
- **`tools/approval.py`** — add session-scoped YOLO state (`_session_yolo` set, guarded by existing `_lock`); helpers: `enable_session_yolo`, `disable_session_yolo`, `is_session_yolo_enabled`, `is_current_session_yolo_enabled`; `clear_session` now also discards YOLO state
- **`gateway/run.py`** — `_handle_yolo_command` uses session-scoped helpers instead of `os.environ`
- **`check_dangerous_command` + `check_all_command_guards`** — now check session-scoped YOLO in addition to env var
- CLI `--yolo` remains unchanged (process-scoped via env var)

## Tests
- `tests/gateway/test_yolo_command.py` — gateway session isolation (chat-a gets YOLO, chat-b doesn't, env var untouched)
- `tests/tools/test_yolo_mode.py` — session-scoped bypass in dangerous command + combined guard + cleanup

All 10 new tests + 123 existing approval tests pass. E2E verified with real imports.

 — contributor commit preserved via cherry-pick.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_yolo_command.py`
- `tests/tools/test_yolo_mode.py`