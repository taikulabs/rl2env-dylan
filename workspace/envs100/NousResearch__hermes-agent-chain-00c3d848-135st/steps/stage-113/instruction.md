**fix(anthropic): remove Claude Code fingerprinting from OAuth Messages API path**

## Summary
OAuth Anthropic requests now identify as Hermes on the wire. The Claude Code spoofing layer (PR #1597, Mar 2026) is gone from the Messages API path; live-verified against api.anthropic.com with a fresh sk-ant-oat01-\* token.

## What changed
- **Removed (cosmetic identity spoofing):**
  - `You are Claude Code...` system-prompt prepend
  - `Hermes Agent`→`Claude Code`, `Nous Research`→`Anthropic` system substitutions
  - `mcp_` tool-name prefix on outgoing schemas + message history
  - Matching `mcp_` strip on inbound `tool_use` blocks (`strip_tool_prefix` path + all 5 call sites in `run_agent.py` and `auxiliary_client.py`)
  - `user-agent: claude-cli/<v> (external, cli)` and `x-app: cli` headers on the Messages API client
- **Added:**
  - OAuth path strips `context-1m-2025-08-07` beta — without Claude Code UA, Anthropic returns 400 `This authentication style is incompatible with the long context beta header.` OAuth subscription traffic gets the 200K default window, which matches Claude Code's own behavior.
- **Kept (auth plumbing, not identity spoofing):**
  - `_is_oauth_token` classifier / `is_oauth` threading
  - Bearer vs x-api-key auth routing
  - `_OAUTH_ONLY_BETAS` (`claude-code-20250219`, `oauth-2025-04-20`) — Anthropic requires these on the OAuth-gated Messages endpoint
  - `_OAUTH_CLIENT_ID` (Claude Code's) — Anthropic doesn't issue OAuth creds to third parties
  - `claude-cli/<v>` UA on `platform.claude.com/v1/oauth/token` (login + refresh only) — bare requests get Cloudflare 1010 blocked

## Validation
| | Before (spoofed) | After (realigned) |
|---|---|---|
| Messages API / OAuth / simple call | HTTP 200 | HTTP 200 ✅ live-verified |
| Messages API / OAuth / tool call | HTTP 200, `mcp_terminal` round-trip | HTTP 200, `terminal` round-trip ✅ live-verified |
| System prompt on wire | `You are Claude Code...\nYou are Claude Code by Anthropic.` | `You are Hermes Agent by Nous Research.` |
| Tool names on wire | `mcp_terminal`, `mcp_read_file`, ... | `terminal`, `read_file`, ... |
| User-Agent on Messages | `claude-cli/2.1.74 (external, cli)` | `python-httpx/*` (SDK default) |
| User-Agent on OAuth token endpoints | `claude-cli/...` | **unchanged** (Cloudflare gate) |
| `context-1m` beta on OAuth | sent (accepted under spoof) | stripped |

Targeted tests: 239 passed + 2 new regression tests covering the no-spoofed-headers and context-1m-strip invariants. 2 pre-existing change-detector failures on main are unrelated.

## Live test
Ran a real OAuth-auth Messages request with Hermes identity in system and a tool named `terminal`:

```
stop_reason=tool_use  in=580 out=53
TOOL: name='terminal' input={'command': 'echo hello'}
```

No "you must use extra usage" gate, no 500s, no 401.

## Closes / supersedes
- #16820 (the `mcp_` PascalCase normalization patch) — the entire `mcp_` round-trip is gone, so the PascalCase dispatch failure it fixed can no longer occur on this path.