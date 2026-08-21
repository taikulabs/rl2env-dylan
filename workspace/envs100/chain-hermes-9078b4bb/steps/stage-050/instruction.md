**fix(terminal): bridge docker_extra_args to TERMINAL_DOCKER_EXTRA_ARGS in CLI + gateway**

## Summary

`terminal.docker_extra_args` passes flags verbatim to `docker run` (e.g. `--gpus=all`, `--shm-size=16g`). It is wired into:

- `DEFAULT_CONFIG["terminal"]` (`hermes_cli/config.py`)
- `TERMINAL_CONFIG_ENV_MAP` — so `hermes config set terminal.docker_extra_args …` bridges it to `.env`
- `tools/terminal_tool.py::_get_env_config()` — reads `TERMINAL_DOCKER_EXTRA_ARGS`
- `tools/environments/docker.py` — applies `extra_args` to the `docker run` command

…but it was **missing from the other two yaml→env bridges**: `cli.py`'s `env_mappings` and `gateway/run.py`'s `_terminal_env_map`.

## Symptom

A user reported (Hermes Desktop on Windows, `terminal.backend=docker`) that Hermes "partially reads the Docker config": `image` and `volume` are honored, but `--gpus=all` and `--shm-size=16g` are silently dropped from the generated `docker run` command.

Root cause: the user **hand-edited `config.yaml`** rather than running `hermes config set`. On the CLI and gateway/desktop startup paths, `docker_extra_args` never reaches `os.environ` because neither bridge maps it — while `docker_image`/`docker_volumes` (which *are* in those maps) bridge fine. `_get_env_config()` reads only `TERMINAL_*` env vars at runtime, so the flags vanish before `DockerEnvironment` ever sees them.

This is the **same bridge-coverage bug class** that already shipped twice — `docker_run_as_host_user` (missing from cli + gateway) and `docker_mount_cwd_to_workspace` (missing from gateway).

## Fix

- Add `"docker_extra_args": "TERMINAL_DOCKER_EXTRA_ARGS"` to `cli.py`'s `env_mappings` and `gateway/run.py`'s `_terminal_env_map`.
- Add `test_docker_extra_args_is_bridged_everywhere` to `tests/tools/test_terminal_config_env_sync.py`, mirroring the existing `test_docker_*_is_bridged_everywhere` regression pins (asserts the key is present in all three bridge maps **and** consumed by `terminal_tool`).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_terminal_config_env_sync.py`