**fix(gateway): salvage 6 gateway fix PRs #6942 #6935 #6921 #6897 #6853 #6811**

## Summary

Salvage of 6 gateway fix PRs onto current main. All contributor authorship preserved via cherry-pick.

**Cherry-picked commits:**

- **#6942** (aquaright1) — Introduces `ProcessingOutcome` enum (SUCCESS/FAILURE/CANCELLED) replacing boolean `success` param in `on_processing_complete()`. Prevents false ❌ failure reactions on Discord/Telegram/Matrix when gateway restarts cancel background tasks.

- **#6935** (Tranquil-Flow) — Adds "background" to the active-session bypass list in `base.py` and early dispatch in `run.py`. Without this, `/background` gets queued as a pending message when an agent is running. **Only the 3-file fix was cherry-picked** — the PR's ~660 lines of unrelated changes (Mnemoria plugin, browser/vision/RL fixes) were excluded.

- **#6921** (Cafexss) — Replaces `assert` with `if/raise RuntimeError` in `telegram_network.py` and `feishu.py`. Under `python -O`, asserts are stripped, causing confusing TypeErrors.

- **#6897** (borischou) — Increases HTTPX pool sizes/timeouts for Telegram adapter, makes them env-configurable, creates separate HTTPXRequest instances for request vs get-updates to reduce contention, skips fallback-IP transport when proxy is configured.

- **#6853** (KUSH42) — Fixes duplicate message flood on platforms without message IDs (Signal, webhooks). The `__no_edit__` sentinel was being reset on every tool-call boundary, re-entering the "first send" path. Also repairs 3 pre-existing test failures.

- **#6811** (Dusk1e) — Centralizes PID termination into `terminate_pid()` helper in `gateway/status.py` using `taskkill` on Windows instead of `SIGKILL` (which doesn't exist there).

**Also closed (not merged):**
- **#6941** — Already addressed by  (path remapping in systemd unit)
- **#6812** — Bug not real; `refresh_launchd_plist_if_needed()` already does bootout+bootstrap internally

## Test results
- 246 passed across affected gateway test files
- 6 pre-existing failures in `test_run_progress_topics.py` (missing `_session_model_overrides` attribute — `object.__new__()` test pattern issue, exists on main)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_runner_startup_failures.py`
- `tests/gateway/test_status.py`
- `tests/hermes_cli/test_gateway.py`