**fix(mcp-oauth): port mismatch, path traversal, and shared handler state (salvage #2521)**

## Summary



Fixes three bugs in the MCP OAuth 2.1 PKCE implementation (`tools/mcp_oauth.py`):

1. **Port mismatch (CRITICAL):** `build_oauth_auth()` and `_wait_for_callback()` each called `_find_free_port()` independently, getting different ports. Browser redirected to port A, server listened on port B → 120s timeout. Fix: share port via module-level `_oauth_port`.

2. **Path traversal (MEDIUM):** `HermesTokenStorage` used `server_name` directly in file paths. A name like `../../.ssh/config` could escape `~/.hermes/mcp-tokens/`. Fix: `_sanitize_server_name()` regex sanitization.

3. **Class-level state (LOW):** `_CallbackHandler` stored auth state as class attributes, causing data races in concurrent flows. Fix: factory function `_make_callback_handler()` with closure-scoped result dict.

## Tests
- 17 tests pass (10 existing + 7 new covering all three fixes)

Original author: @0xbyt4 — commits cherry-picked with authorship preserved.
