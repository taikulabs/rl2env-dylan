**fix(acp): thread-safe interactive approval via contextvars**

## Summary
Concurrent ACP sessions can no longer race on the interactive-approval flag — a dangerous command can never slip onto the auto-approve path because of a neighboring session.

**Root cause:** `acp_adapter/server.py` runs a `ThreadPoolExecutor(max_workers=4)`, so up to four ACP sessions run concurrently. Each `_run_agent` set the **process-global** `os.environ["HERMES_INTERACTIVE"] = "1"` and restored it in `finally`. One session's restore could clobber another session's set mid-run, dropping the second session onto the non-interactive **auto-approve** branch in `tools.approval` — a dangerous command then executes without the approval callback ever firing (GHSA-96vc-wcxf-jjff pattern).

## Changes
- `tools/approval.py`: new thread/task-local `_hermes_interactive_ctx` contextvar + `set_hermes_interactive_context()` / `reset_hermes_interactive_context()`. Both `HERMES_INTERACTIVE` read sites now go through `_is_interactive_cli()` — contextvar-first, env-var fallback for legacy single-threaded CLI callers.
- `acp_adapter/server.py`: the executor sets the contextvar instead of mutating `os.environ`; restore in `finally` uses `reset_hermes_interactive_context`. The existing `contextvars.copy_context()` wrapper isolates each session's write.
- `tests/acp/test_approval_isolation.py`: added a test proving the contextvar routes dangerous commands through the callback with no `HERMES_INTERACTIVE` in the environment.

## Validation
| | Before | After |
|---|---|---|
| Interactive flag | process-global `os.environ` | thread/task-local contextvar |
| Concurrent ACP sessions | can clobber each other's flag | isolated per `copy_context()` |
| Legacy CLI (`HERMES_INTERACTIVE`) | works | works (env fallback) |
| `tests/acp/test_approval_isolation.py` | — | 8/8 pass |
| E2E race repro (2 threads, opposite flags, barrier-forced interleave) | — | zero cross-contamination |

Salvaged from #15653 by @georgex8001 — the original branch was far behind `main` and its `tools/approval.py` diff was written against an old version of the file (it would have reverted current observability contextvars, `_YOLO_MODE_FROZEN`, and gateway-routing helpers). The narrow contextvar fix and the contributor's test were reapplied cleanly onto current `main` with authorship preserved.

## Infographic
![Thread-safe ACP approval via contextvars](https://v3b.fal.media/files/b/0aa05be0/pk6M0uNEbuNnApr7rp4zU_yOyAVOes.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/acp/test_approval_isolation.py`