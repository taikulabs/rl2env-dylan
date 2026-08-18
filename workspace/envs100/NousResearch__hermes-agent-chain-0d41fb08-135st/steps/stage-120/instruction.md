**feat: add --env and --preset support to hermes mcp add**

## Summary
Salvage of PR #7936 by @syaor4n, with stitch preset removed per maintainer direction.

Adds two new flags to `hermes mcp add`:

**`--env KEY=VALUE`** — Pass environment variables to stdio MCP servers. Validated with POSIX env var name rules. Rejected for HTTP servers.

**`--preset <name>`** — Use a known MCP server template to fill in command/args automatically. Currently ships with an empty preset registry (`_MCP_PRESETS` dict in `mcp_config.py`) — ready for community presets to be added over time. Explicit `--command`/`--url` overrides preset defaults.

## Changes
- `hermes_cli/mcp_config.py`: `_parse_env_assignments()`, `_apply_mcp_preset()`, empty `_MCP_PRESETS` dict, integration into `cmd_mcp_add()`
- `hermes_cli/main.py`: `--preset` and `--env` argparse arguments
- `tests/hermes_cli/test_mcp_config.py`: 6 new tests (env passthrough, invalid env name, HTTP rejection, preset fills transport, explicit overrides preset, unknown preset rejected)
- Removed unused `import getpass`

## Test Results
- `test_mcp_config.py`: 28 passed