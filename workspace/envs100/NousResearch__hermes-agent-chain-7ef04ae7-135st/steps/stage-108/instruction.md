**fix(bg-review): scope stdout/stderr silencing to the worker thread**

## Summary

The background memory/skill review thread no longer blanks `stdout`/`stderr` for the rest of the process while it runs.

Root cause: `agent/background_review.py` wrapped the entire review-thread body in process-global `contextlib.redirect_stdout(devnull)` / `redirect_stderr(devnull)`. Those rebind `sys.stdout`/`sys.stderr` for the whole process, so for the full duration of a review (tens of seconds) every *other* thread — including a gateway event-loop thread driving a Telegram long-poll — also wrote to devnull. Any bare `print` / `sys.stderr.write` from those threads during the window was silently lost. This is the cross-thread output hazard surfaced while investigating #55769 / #55925 (the silent Telegram poller death).

## Changes

- `agent/thread_scoped_output.py` (new): `thread_scoped_silence()` — installs a per-thread routing proxy once as `sys.stdout`/`sys.stderr`. Only threads registered as silenced write to devnull; every other thread passes through to the original stream. Depth-counted so nested use on the same thread composes. Never uninstalled (uninstalling would race other threads mid-write) — unregistered threads pay only one attribute lookup per write.
- `agent/background_review.py`: replace both global-redirect sites (main body + exception-path teardown) with `thread_scoped_silence()`; drop the now-unused `contextlib` import.
- `tests/agent/test_thread_scoped_output.py` (new): 6 behaviour tests.

## Validation

| Scenario | Before (global redirect) | After (thread-scoped) |
|---|---|---|
| bg-review thread output | dropped | dropped |
| concurrent thread writing *during* the review window | **dropped** | survives |
| main thread output during review | **dropped** | survives |
| nested silence, same thread | broken | depth-counted |

`scripts/run_tests.sh tests/agent/test_thread_scoped_output.py` + the four existing `background_review` / review-summary suites: all green.

Scope note: this fixes the cross-thread *output* hazard only. The Telegram poller self-heal is #55905 (already merged); the remaining trigger follow-ups (ladder breadcrumb visibility, httpx pool sharing check) ship separately.

## Infographic

![thread-scoped-output-silencing](https://v3b.fal.media/files/b/0aa06f3f/ng81wHPd2LctZjS-Uj9Ty_N041FfqB.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_thread_scoped_output.py`