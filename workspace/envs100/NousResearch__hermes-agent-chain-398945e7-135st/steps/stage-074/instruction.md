**fix(gateway): auto-restart when source files change out from under us**

. Supersedes #17935.

## Summary
Gateway processes that survive `hermes update` now detect stale code on their next inbound message and trigger a graceful restart, instead of serving `ImportError` responses until the user notices and runs `hermes gateway restart` by hand.

## Root cause
A long-running gateway that isn't killed during `hermes update` keeps pre-update modules cached in `sys.modules`. When the updated tool files on disk then import a name added post-update — e.g. `cfg_get` from PR #17304 — the import resolves against the already-loaded stale module object and raises `ImportError`. Five independent reports on #17648 (Matrix, Telegram, Feishu) all fixed it with `hermes gateway restart`.

## Changes
- `gateway/run.py` — on `__init__`, snapshot newest mtime across five sentinel source files (`hermes_cli/config.py`, `hermes_cli/__init__.py`, `run_agent.py`, `gateway/run.py`, `pyproject.toml`). On every inbound `_handle_message`, re-read; if newer than boot + 2s slack, call `request_restart(via_service=True)` and return a one-line ack. Idempotent (fires at most once per process). Class-level defaults so partial-construction tests keep working.
- `hermes_cli/main.py` — after the existing post-update gateway restart loop, sleep 3s and rescan `find_gateway_pids(all_profiles=True)`. Any PID we already tried to kill that's still alive gets SIGKILLed so the watcher / service manager can relaunch with fresh code instead of waiting out the 120s watcher timeout.
- `tests/gateway/test_stale_code_self_check.py` — 12 tests covering `_compute_repo_mtime`, `_detect_stale_code` (positive, negative, slack, missing files, disappearing repo), `_trigger_stale_code_restart` (idempotence, error tolerance), and class-level default safety.

## Why not PR #17935's approach
#17935 wrapped every `from hermes_cli.config import cfg_get` in a try/except fallback — 19 files, 266 duplicated lines. That treats the symptom (import fails) and hides the underlying state mismatch (gateway is running old code). A stale gateway has many more problems than just this one import: old `DEFAULT_CONFIG`, old migrations, old `OPTIONAL_ENV_VARS`. Detecting and restarting is the right layer.

## Validation
| | Before | After |
|---|---|---|
| Gateway survives `hermes update` | `ImportError` on next message | Auto-restart + ack; back up in seconds |
| Stuck PID ignores SIGTERM | Watcher waits 120s, often gives up | `hermes update` SIGKILLs after 3s |
| `/restart` still works | ✓ | ✓ (both paths route through `request_restart`) |

Unit + E2E tests: `scripts/run_tests.sh tests/gateway/test_stale_code_self_check.py` → 12/12 pass; `test_update_command.py` → 28/28 pass; `test_background_command.py test_session_boundary_security_state.py test_command_bypass_active_session.py` → 64/64 pass.

E2E harness (outside pytest) simulated an update by bumping `hermes_cli/config.py` mtime on a real repo and confirmed `_detect_stale_code()` returned True against a 120s delta.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_stale_code_self_check.py`