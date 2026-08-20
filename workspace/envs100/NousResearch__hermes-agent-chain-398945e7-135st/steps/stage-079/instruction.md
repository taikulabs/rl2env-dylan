**fix(constants): warn once when get_hermes_home() falls back under an active profile**

Makes the ~/.hermes fallback visible when a non-default profile is active. Surfaces cross-profile data contamination without breaking the 30+ module-level callers that import `get_hermes_home()` at load time.

## What changed
- `hermes_constants.py`: when `HERMES_HOME` is unset and `~/.hermes/active_profile` names a non-default profile, write a one-shot warning to stderr and continue returning `~/.hermes` as before.
- `tests/test_hermes_home_profile_warning.py`: 6 test cases (classic mode, default profile, named profile, env-set-wins, unreadable active_profile, empty active_profile).

## Why not raise (superseding #18600)
The original PR proposal raised `ValueError` from `get_hermes_home()` when a named profile was active without `HERMES_HOME` set. 30+ files call this at module-import scope (`run_agent.py`, `gateway/run.py`, `cron/scheduler.py`, `hermes_cli/doctor.py`, `tools/skills_tool.py`, `acp_adapter/entry.py`, etc.) — raising there would brick imports in every cron tick, subagent, and IDE launcher where HERMES_HOME didn't propagate for any reason. That failure mode is worse than the silent bleed it fixes. POSIX subprocesses actually DO inherit parent env by default, so the real propagation paths (systemd unit `Environment=`, kanban dispatcher `env=dict(os.environ)`, docker entrypoint) already work.

The stderr write bypasses `logging` because this function runs before logging is configured in many of the import-time callers, and going through the root logger double-emits on consoles that already have a StreamHandler.

## Validation
- `scripts/run_tests.sh tests/test_hermes_home_profile_warning.py tests/hermes_cli/test_profiles.py` → 100 passed.
- E2E: real `HOME` redirect + `active_profile=coder` + `HERMES_HOME` unset. 10 calls to `get_hermes_home()` → exactly 1 warning emitted to stderr, fallback path still returned, module imports of `hermes_cli.gateway` and `cron.scheduler` succeed.

. Credit to @liuhao1024 for surfacing the silent-fallback case in #18600.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_hermes_home_profile_warning.py`