**fix(mcp-oauth): preserve server_url path for protected-resource validation**

.

## Summary
MCP OAuth now preserves the path component of the configured server URL so path-scoped Protected Resource Metadata (Notion MCP, `https://mcp.notion.com/mcp`) validates correctly.

## Root cause
`tools/mcp_oauth.py` defined `_parse_base_url()` and applied it to `server_url` right before constructing `OAuthClientProvider`, collapsing `https://mcp.notion.com/mcp` → `https://mcp.notion.com`. The MCP SDK then:
- used the (already stripped) `server_url` for RFC 8707 canonical resource via `resource_url_from_server_url()`
- passed it to `check_resource_allowed(requested, configured)` against Notion's PRM resource `https://mcp.notion.com/mcp`

Hierarchical match fails (requested `/` shorter than configured `/mcp/`) → `Protected resource https://mcp.notion.com/mcp does not match expected https://mcp.notion.com`.

The SDK strips the path itself where needed (for authorization-server discovery, via `OAuthContext.get_authorization_base_url()` at `mcp/client/auth/oauth2.py:320,365,426,578`). Our pre-stripping was redundant for discovery AND destructive for PRM validation.

## Changes
- `tools/mcp_oauth.py`: delete `_parse_base_url`, pass `server_url` through to `OAuthClientProvider` unmodified.
- `tools/mcp_oauth_manager.py`: drop the `_parse_base_url` import, pass `entry.server_url` directly.
- `tests/tools/test_mcp_oauth.py`: drop `test_parse_base_url_strips_path`, add `test_build_oauth_auth_preserves_server_url_path` — captures the kwargs passed to a fake `OAuthClientProvider` and asserts the full URL (including `/mcp`) is forwarded verbatim.

## Validation
| | Before | After |
|---|---|---|
| `server_url` forwarded to `OAuthClientProvider` for `https://mcp.notion.com/mcp` | `https://mcp.notion.com` | `https://mcp.notion.com/mcp` |
| `tests/tools/test_mcp_oauth.py` | 37 passed | 37 passed |
| `tests/tools/test_mcp_oauth_{manager,integration,bidirectional,cold_load_expiry}.py` | — | 23 passed |

Regression test verified by reverting the fix in-place: new test fails with `AssertionError: 'https://mcp.notion.com' == 'https://mcp.notion.com/mcp'`, which maps 1:1 to the user's reported error. Fix restored, suite re-green.