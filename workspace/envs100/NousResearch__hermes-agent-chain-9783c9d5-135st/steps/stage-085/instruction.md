**feat(mcp): dynamic tool discovery via notifications/tools/list_changed**

## Summary

Implement MCP spec's `notifications/tools/list_changed` notification handler. When a connected MCP server sends this notification (e.g., GitHub MCP with `GITHUB_DYNAMIC_TOOLSETS=1`), Hermes automatically re-fetches the tool list, deregisters removed tools, and registers new ones — without requiring a gateway restart or `/mcp refresh`.

### Changes

**`tools/registry.py`**
- `ToolRegistry.deregister(name)` — removes a tool and cleans up its toolset check if it was the last tool in that toolset. Used by the nuke-and-repave refresh strategy.

**`tools/mcp_tool.py`**
- Notification type imports (`ToolListChangedNotification`, `ServerNotification`, etc.) with graceful degradation for older SDK versions
- `_check_message_handler_support()` — inspects `ClientSession` constructor to verify the SDK version accepts `message_handler`
- `_register_server_tools()` — extracted from `_discover_and_register_server()` as a shared helper used by both initial discovery and dynamic refresh. Handles filtering, collision guards, utility tools, toolset creation, and hermes-* injection.
- `MCPServerTask._make_message_handler()` — builds a notification callback that dispatches on type; `ToolListChangedNotification` triggers refresh, prompt/resource changes are logged stubs
- `MCPServerTask._refresh_tools()` — nuke-and-repave under `_refresh_lock`: fetch new tools, remove old from registry + hermes-* toolsets, re-register fresh
- `message_handler` wired into all 3 `ClientSession` construction sites (stdio, new HTTP, deprecated HTTP)

**`tests/tools/test_mcp_dynamic_discovery.py`** (new, 8 tests)
- Registration → hermes-* injection
- Full refresh cycle (old removed, new registered)
- Message handler dispatch
- `deregister()` edge cases

### Backward compatibility

- If the MCP SDK lacks notification types or `message_handler` support, the feature silently degrades to existing static-discovery behavior
- No new config keys needed — activates automatically when a server sends the notification
- `mcp_servers` config format is unchanged

Salvaged from PR #1794 by @shivvor2.