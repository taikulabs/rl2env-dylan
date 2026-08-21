**fix: auto-reload MCP tools when mcp_servers config changes without restart**

## Summary
- auto-reload MCP connections when `mcp_servers` changes in `config.yaml`
- keep `/reload-mcp` as the manual fallback
- add focused regression coverage for the config watcher path

## Notes
- salvages the substantive fix from PR #1048 onto current `main`
- preserves contributor authorship via cherry-pick

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_cli_mcp_config_watch.py`