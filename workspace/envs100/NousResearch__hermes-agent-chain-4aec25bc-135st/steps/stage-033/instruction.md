**fix(teams): fall back to default port on invalid port config (salvage #27167)**

## Summary
Salvage of #27167 — invalid `TEAMS_PORT` env var or `platforms.teams.extra.port` config (e.g. `"abc"`) crashed `TeamsAdapter.__init__` with `ValueError` instead of falling back to the default port 3978.

## Changes
- `plugins/platforms/teams/adapter.py` — add `_coerce_port()` helper that wraps `int()` in try/except and returns the default on bad input.
- `tests/gateway/test_teams.py` — two regression tests covering bad `extra.port` and bad `TEAMS_PORT` env var.

## Validation
- `scripts/run_tests.sh tests/gateway/test_teams.py -q` → 46/46 pass.

Original PR: #27167 — credit preserved via rebase-merge.