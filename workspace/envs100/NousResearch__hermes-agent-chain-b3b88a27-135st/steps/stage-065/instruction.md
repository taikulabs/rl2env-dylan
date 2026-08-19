**fix(gateway): allow systemd-backed distrobox services**

Salvage of #11845 onto current main (authorship preserved via cherry-pick).

## Summary
`hermes gateway install/start` now works inside distrobox and other containerized Linux environments that expose a real systemd session, instead of always short-circuiting to the Docker/Podman "run manually" path.

## Changes
- `hermes_cli/gateway.py`: new `_systemd_operational(system=bool)` helper (WSL probe delegates to it); new `_container_systemd_operational()` that checks user scope then system scope; `supports_systemd_services()` now calls the container probe instead of returning False for all containers.
- `tests/hermes_cli/test_gateway.py`: 5 new tests covering the container-with-user-systemd, container-with-system-systemd, container-without-systemd, and install/start dispatch paths.

## Validation
| | Before | After |
|---|---|---|
| Distrobox `gateway install` | prints Docker guidance, exits | runs `systemd_install` |
| Distrobox `gateway start` | prints Docker guidance, exits | runs `systemd_start` |
| Docker-without-systemd | prints Docker guidance | unchanged |
| WSL / macOS / Termux / bare Linux | unchanged | unchanged |

`scripts/run_tests.sh tests/hermes_cli/test_gateway.py tests/hermes_cli/test_gateway_wsl.py tests/test_hermes_constants.py` → 51 passed.

Credit to @helix4u — original PR #11845.