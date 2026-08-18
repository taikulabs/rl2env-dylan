**fix(security): block untrusted browser-origin API server access (salvage #2108)**

## Summary
Salvage of PR #2108 by @ifrederico, cherry-picked onto current main.

**Security issue:** The API server had `Access-Control-Allow-Origin: *` on all responses. Since the API server gives full terminal access, any website a user visits could make cross-origin requests to the locally running API server and execute arbitrary commands.

### Fix
- Removes default wildcard CORS (`*`)
- Browser-originated requests (those with `Origin` header) are now rejected with 403 by default
- New `API_SERVER_CORS_ORIGINS` env var / config option to explicitly allowlist browser origins
- Non-browser requests (curl, server-to-server like Open WebUI) continue to work unchanged
- Proper `Vary: Origin` header for non-wildcard CORS responses
- Wildcard mode still available via `API_SERVER_CORS_ORIGINS=*` for users who explicitly want it

### Changes
- `gateway/platforms/api_server.py`: `_origin_allowed()`, `_cors_headers_for_origin()`, `_parse_cors_origins()` methods; middleware updated to check adapter
- `gateway/config.py`: `API_SERVER_CORS_ORIGINS` env override
- `tests/gateway/test_api_server.py`: 12 new CORS tests (default rejection, allowlist, preflight, non-browser passthrough)
- Docs: api-server.md, open-webui.md, environment-variables.md updated

### Skipped
The second commit (ASCII→Mermaid diagram swap in open-webui.md) was skipped due to conflict — cosmetic only.

## Verification
- 5789 passed (pre-existing failures identical to clean main)
- API server tests: 82/82 passed

## Credit
Original work by @ifrederico in #2108. Contributor authorship preserved via cherry-pick.