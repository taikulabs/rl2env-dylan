**fix(cron): preserve skill env passthrough in worker thread**

## Summary

When a cron job loads a skill that declares `required_environment_variables` (e.g. `NOTION_API_KEY`), those vars get registered in a `ContextVar`-based allowlist for sandbox passthrough. But the cron agent runs inside a `ThreadPoolExecutor` worker thread, and Python's `ThreadPoolExecutor.submit()` does **not** propagate `ContextVar` state. The skill's env vars are registered in the scheduler thread's context but invisible in the worker thread where the agent executes.

**Fix:** `contextvars.copy_context()` before submitting, then `ctx.run(agent.run_conversation, prompt)` in the worker thread. This is the standard Python pattern for ContextVar propagation into thread pools.

**Bonus:** This also propagates `credential_files.py`'s `_registered_files_var` ContextVar — skills declaring `required_credential_files` now correctly pass those through in cron jobs too.

## Changes

- `cron/scheduler.py`: 4-line fix — `contextvars.copy_context()` + `ctx.run()` wrapper
- `tests/cron/test_scheduler.py`: regression test verifying env passthrough propagates into the worker thread