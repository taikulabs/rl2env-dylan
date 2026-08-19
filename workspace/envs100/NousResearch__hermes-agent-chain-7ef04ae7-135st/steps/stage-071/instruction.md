**fix(mcp): late-refresh must see desktop/dashboard discovery thread owner**

## Summary
MCP server tools now surface into the agent's session toolset on the desktop app and dashboard WebUI, fixing #51587.

Root cause: a slow MCP server (one that finishes connecting after the bounded build-time discovery wait) was never caught by the automatic late-refresh on the desktop/dashboard surfaces, so its tools stayed invisible for the whole session — even across container restarts. The `platform_toolsets` config having no MCP entry is a red herring; `_get_platform_tools(..., include_default_mcp_servers=True)` already auto-appends every enabled MCP server.

## The bug
There are two independent background MCP discovery thread owners by surface:

- `tui_gateway.entry` — stdio `hermes --tui`.
- `hermes_cli.mcp_startup` — desktop app + dashboard WebSocket sidecar (`tui_gateway/ws.py`) and `hermes dashboard`.

`tui_gateway.server._schedule_mcp_late_refresh` gates on `tui_gateway.entry.mcp_discovery_in_flight()`, which read **only** `tui_gateway.entry._mcp_discovery_thread`. On the desktop/dashboard surfaces that global is `None` (the live thread lives on `hermes_cli.mcp_startup`), so the scheduler bailed immediately. The stdio TUI path worked because it populates the entry global directly — matching the report (CLI recovers via `/reload-mcp`; desktop never does).

## Changes
- `hermes_cli/mcp_startup.py`: add `mcp_discovery_in_flight()` / `join_mcp_discovery()` for the thread it owns.
- `tui_gateway/entry.py`: `mcp_discovery_in_flight()` / `join_mcp_discovery()` now consult **both** owners.
- `tests/tui_gateway/test_mcp_late_refresh_thread_owner.py`: regression coverage for both surfaces + no-MCP case.

Cache-safe: the late refresh already only rebuilds pre-first-turn, so it never invalidates a cached prompt prefix mid-conversation.

## Validation
| | Before | After |
|---|---|---|
| Desktop/dashboard, slow MCP server | `in_flight()` → False → late refresh bails → tools missing all session | consults startup thread → late refresh fires → tools surface automatically |
| Stdio `hermes --tui` | works | unchanged |
| No MCP configured | not in flight | not in flight |

10 tests green (5 new + 5 existing `test_mcp_startup.py`). Bug confirmed on pre-fix logic and fix verified via isolated E2E.

## Infographic
![infographic](https://v3b.fal.media/files/b/0aa05935/sNaEbqkJKQD4099NZYUTT_rLy11u1h.png)

Reported by @itsAlice92, additional desktop data points from @koloved.