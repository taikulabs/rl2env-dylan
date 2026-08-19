**fix(mcp-oauth): print SSH tunnel hint in _redirect_handler (salvage #26674)**

## Summary
Salvage of #26674 — `_redirect_handler` in `tools/mcp_oauth.py` was missing the SSH tunnel hint that #26592 added for xAI/Spotify OAuth. On a remote SSH session the MCP OAuth provider redirects to `http://127.0.0.1:<port>/callback` — which only the remote machine's listener catches — and without a port-forward, the flow silently times out.

## Changes
- `tools/mcp_oauth.py` — print a port-forward hint when `_oauth_port` is set and `SSH_CLIENT`/`SSH_TTY` is in the env (same gate as the existing `_can_open_browser()` SSH detection).
- `tests/tools/test_mcp_oauth.py` — 4 cases: SSH_CLIENT shows hint, SSH_TTY shows hint, local session does not, port-not-set does not.

Mirrors the existing pattern from #26592. Links to the OAuth-over-SSH docs page.

## Validation
- `scripts/run_tests.sh tests/tools/test_mcp_oauth.py -q` → 42/42 pass.

Original PR: #26674 — credit preserved via rebase-merge.