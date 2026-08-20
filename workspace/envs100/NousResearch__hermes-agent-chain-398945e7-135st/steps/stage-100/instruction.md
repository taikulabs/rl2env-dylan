**fix(api_server): fall back to default port on malformed API_SERVER_PORT**

Salvage of #19353 by @Zyproth onto current main.

## Summary
`APIServerAdapter.__init__` was re-reading `API_SERVER_PORT` raw and calling `int(...)` unguarded, crashing startup on malformed values. `gateway.config._apply_env_overrides()` already handles this defensively. Adds the same coercion guard to the adapter so malformed env/config values fall back to the default port instead of crashing.

## Changes
- gateway/platforms/api_server.py: `_coerce_port()` helper + guarded init (+13/-1)
- tests: regression for invalid port → default port

## Validation
scripts/run_tests.sh tests/gateway/test_api_server.py → 125 passed

Original PR: #19353

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_api_server.py`