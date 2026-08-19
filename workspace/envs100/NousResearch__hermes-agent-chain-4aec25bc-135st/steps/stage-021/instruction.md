**fix(mcp): validate remote URLs up-front with a clear error (salvage of #18132)**

## Summary
Salvage of #18132 — typos in MCP server URLs (missing scheme, wrong scheme, empty string, non-string) now fail fast with a clear error naming the offending server, instead of burning ~60s of exponential backoff with an opaque exception inside the transport layer.

Port from anomalyco/.

## Root cause
`tools/mcp_tool.py` `_run_http()` passes `config["url"]` verbatim to `httpx.URL(url)`. A malformed URL raises a generic exception deep in the transport, which gets swallowed by the reconnect-backoff loop (`while True: try: ... except Exception:`). The bad URL costs ~60s of pointless retries with a confusing error before the server is finally marked failed.

## Salvage notes
Branch was 1,677 commits stale. One conflict in `tools/mcp_tool.py`: main added MCP image-block helpers between this PR's branch point and now, at the same line where the PR was adding the URL-validation helpers. Both kept (independent additions in different concern areas — image-block caching vs URL validation).

## Changes
- `tools/mcp_tool.py` (+61): new `InvalidMcpUrlError(ValueError)` + `_validate_remote_mcp_url(server_name, url)` (scheme must be http/https, host must be non-empty, value must be a string). Wired into `MCPServerTask.run()` before the retry loop — malformed URLs short-circuit immediately with `_error` set and `_ready` fired so `start()` re-raises the clean error.
- `tests/tools/test_mcp_invalid_url.py` (+143): 21 cases covering valid URL acceptance (IPv4, IPv6, ports, query) and every rejection path; `InvalidMcpUrlError` is a `ValueError`; error message names the server.

## Validation
| | Before | After |
|---|---|---|
| Bad URL (`not-a-valid-url`) | ~60s of silent retries, opaque error | <0.01ms, `Invalid MCP URL for 'broken': scheme must be http or https…` |
| Valid URL | Works | Works (unchanged) |
| stdio server (`command`, no `url`) | Skipped | Still skipped (`_is_http()` is False) |

- `tests/tools/test_mcp_invalid_url.py` — 21/21
- `tests/tools/test_mcp_tool.py` (regression) — 193/193
- E2E: 4 valid URL forms accepted, 9 invalid rejected in microseconds with server-naming errors

## Architectural note
OpenCode's fix returned `{ client: undefined, status: { status: "failed", error: ... } }`. Hermes uses the existing `_error` / `_ready` pattern for the same outcome — the caller `start()` awaits `_ready` and re-raises `_error`, so `hermes mcp list` shows the server as failed with the clear message. No new public API surface.

## Source
anomalyco/. Originally scouted in #18132.