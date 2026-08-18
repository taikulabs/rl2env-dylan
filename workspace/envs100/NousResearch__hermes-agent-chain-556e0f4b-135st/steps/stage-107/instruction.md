**fix(gateway): detect virtualenv path instead of hardcoding venv/**

## Summary

Salvaged from PR #2493 by @Mibayy (submitted first, cleanest implementation).

**Problem:** `get_python_path()` and `generate_systemd_unit()` in `hermes_cli/gateway.py` hardcode `venv/` as the virtualenv directory. When the virtualenv is `.venv` (which `setup-hermes.sh` creates), the generated systemd unit has incorrect `VIRTUAL_ENV` and `PATH` environment variables.

**Fix:** Adds `_detect_venv_dir()` helper that:
1. Checks `sys.prefix` first (most reliable — reflects the actually active venv)
2. Falls back to probing `.venv` then `venv` under `PROJECT_ROOT`
3. Returns `None` if no venv found

Both `get_python_path()` and `generate_systemd_unit()` now use this helper instead of hardcoded paths.

.

## Duplicate PRs
- #2493 by @Mibayy — **source of this salvage** (submitted first, best implementation)
- #2500 by @teyrebaz33 — duplicate fix
- #2518 by @devorun — duplicate fix

## Tests
6 new tests covering all detection branches + generated unit content. Full suite: 6096 passed.