**fix(gateway): remap all paths in system service unit to target user's home**

## Summary
When `hermes gateway install` generates a **system** systemd unit via sudo, `ExecStart`, `WorkingDirectory`, `VIRTUAL_ENV`, and `PATH` entries were not remapped to the target user's home — only `HERMES_HOME` was. This caused the service to fail with `status=200/CHDIR` because the target user cannot access `/root/`.

Adds `_remap_path_for_user()` helper and applies it to all path variables in the `if system:` branch of `generate_systemd_unit()`.

## Changes
- `hermes_cli/gateway.py`: New `_remap_path_for_user()` helper + 6 remap calls in the system service branch
- `tests/hermes_cli/test_gateway_service.py`: 4 new tests (3 unit for helper, 1 integration asserting no root paths leak)

## Test results
54 passed (50 existing + 4 new)

Salvaged from #7030 (Tranquil-Flow) and #7016 (ygd58). Contributor authorship preserved.