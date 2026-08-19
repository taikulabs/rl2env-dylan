**fix(cron): layer enabled MCP servers onto per-job enabled_toolsets**

## Problem

A cron job that set `enabled_toolsets` to native toolsets (e.g. `["web", "terminal"]`) silently got **zero MCP tools**, while a job with no per-job list got every globally-enabled MCP server. `_resolve_cron_enabled_toolsets` returned the per-job list verbatim, bypassing the MCP-merge that the platform-fallback branch does via `_get_platform_tools`. `discover_mcp_tools()` registered the MCP tools into the registry, but `get_tool_definitions(enabled_toolsets=...)` kept only the named native toolsets — the agent rejected every `mcp_*` call as "Unknown tool". (R2 of #23997)

## Fix

`_merge_mcp_into_per_job_toolsets` layers MCP membership onto a per-job allowlist with the **same semantics** as `_get_platform_tools`:
- `no_mcp` sentinel → no MCP servers
- one or more MCP server names already listed → treat as an allowlist (add nothing further)
- otherwise → union in every globally-enabled MCP server

To avoid duplicating the "which MCP servers are enabled" computation (the original PR re-implemented it), this **extracts a shared `enabled_mcp_server_names(config)` helper** in `hermes_cli.tools_config` and has BOTH the gateway/CLI platform resolver and the cron per-job resolver call it — so every path agrees on MCP membership (extend, don't duplicate).

## Scope — what was already fixed on main

The issue's **headline** (bare MCP server names rejected, registry never includes them in cron) was **already fixed on main** before the issue was filed (commits `c10fea8d2` server-alias + `04918345e` discover-MCP-before-cron-agent). This PR closes the remaining cron-specific gap (R2). Two smaller residuals are tracked separately, not in scope here:
- R1: `server:*` / `mcp:server` alias notation still rejected (→ #24104).
- R3: silent drop under `quiet_mode` (→ #24104's warning).

## Salvage / credit

Salvaged from **#32788** by @sherman-yang (authorship preserved). Reworked to reuse the shared `enabled_mcp_server_names` helper instead of re-implementing the MCP membership set in `cron/scheduler.py` (the DRY concern flagged in review).

## Tests

`tests/cron/test_scheduler.py` — per-job native allowlist unions in enabled MCP; `no_mcp` opts out; explicit MCP name acts as allowlist. Full `tests/cron/`: 517 passed; `tests/hermes_cli/test_tools_config.py`: 97 passed (the gateway path still resolves MCP identically after the helper extraction).

## Closes

---

## Review-driven changes (/hermes-pr-review, 3 reviewers — verdict: Approve/ship-ready, no Critical)

- **Strengthened the fall-through test:** `test_resolver_empty_per_job_falls_through_to_platform` now stubs `_get_platform_tools` and asserts the platform branch is actually taken with `platform="cron"` and its result returned — was previously a near-tautology (`result is None or isinstance(result, list)`).
- **Documented the enabled-flag semantics:** the shared `enabled_mcp_server_names` docstring now notes a server is enabled unless *explicitly* falsey (false/0/no/off via `_parse_enabled_flag`); a missing/unrecognized flag is treated as enabled — matching prior gateway behavior.

Reviewers confirmed: the `enabled_mcp_server_names` extraction is **behavior-identical** for the gateway (verbatim move of the inline computation, same `_parse_enabled_flag`); the 3 merge branches are correct with proper allowlist exclusion of unnamed enabled servers; merge runs on the per-job branch only (no double-merge with the platform fallback); the lazy import poses no circular-import risk (cron already imports from hermes_cli widely); disabled-toolset subtraction reliably runs last so a disabled MCP server can't sneak back. Both files pass in isolation (cron 517, tools_config 97).

Note: tests assert the resolved toolset-name list (the contract of these pure resolver functions), not end-to-end tool registration — consistent with the existing resolver tests.