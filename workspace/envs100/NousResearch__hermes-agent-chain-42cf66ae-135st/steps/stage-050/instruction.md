**feat(mcp): salvage selective tool loading with utility policies**

## Summary
- salvage the per-server MCP include/exclude/enabled work from PR #986 by @teyrebaz33
- make filtering comprehensive by extending policy to Hermes-added MCP utility tools as well
- register resource/prompt utility tools only when the server actually supports those capabilities
- store the per-server registered subset so repeated discovery and status reporting stay accurate after filtering
- avoid creating empty MCP toolsets when config filters everything out

## Config behavior
Example:

mcp_servers:
  github:
    url: https://mcp.github.com
    tools:
      include: [create_issue, list_issues]
      prompts: false
  stripe:
    url: https://mcp.stripe.com
    tools:
      exclude: [delete_customer]
      resources: false
  legacy:
    url: https://mcp.legacy.internal
    enabled: false

Rules:
- tools.include whitelists server tools
- tools.exclude blacklists server tools
- include takes precedence over exclude
- tools.resources: false disables list_resources / read_resource
- tools.prompts: false disables list_prompts / get_prompt
- utility tools are only registered if the server session exposes the corresponding capability
- enabled: false skips the server entirely

## Contributor credit
This PR salvages the core selective-tool-loading work from #986 onto current main, then extends it to cover the utility-tool caveat and keep discovery/status semantics accurate.

## Validation
- source /home/teknium/.hermes/hermes-agent/.venv/bin/activate && python -m pytest tests/tools/test_mcp_tool.py::TestMCPSelectiveToolLoading -n0 -q
- source /home/teknium/.hermes/hermes-agent/.venv/bin/activate && python -m pytest tests/tools/test_mcp_tool.py -n0 -q
- source /home/teknium/.hermes/hermes-agent/.venv/bin/activate && python -m pytest tests/ -n0 -q