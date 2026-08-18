**fix: auxiliary client skips expired Codex JWT and propagates Anthropic OAuth flag (salvage #2378)**

## Summary

Salvage of PR #2378 by @0xbyt4, cherry-picked onto current main.

### Two bugs fixed:

**1. Expired Codex JWT blocks the auxiliary auto chain**
`_read_codex_access_token()` returned expired JWTs without checking expiry, blocking fallback to working providers (Anthropic, Z.AI, etc.). All side tasks (compression, vision, memory flush) would silently fail with 401. Now decodes JWT `exp` claim and returns `None` for expired tokens so the auto chain continues.

**2. Auxiliary Anthropic client missing OAuth identity transforms**
`_AnthropicCompletionsAdapter` always called `build_anthropic_kwargs(is_oauth=False)` regardless of token type. OAuth tokens need Claude Code identity transforms (system prompt prefix, tool name prefixing) — without them, Anthropic's proxy rejects with 400. Now detects OAuth tokens via `_is_oauth_token()` and propagates through the adapter chain.

### Follow-up fix
Fixed `test_api_key_no_oauth_flag` — original test set `ANTHROPIC_API_KEY` env var but `_try_anthropic()` resolves tokens via `resolve_anthropic_token()`, which has its own resolution chain. Mocking `resolve_anthropic_token` directly ensures the test key actually reaches `_is_oauth_token()`.

### Impact
Only affects users with expired Codex auth + Anthropic OAuth tokens. All other configurations unchanged.

**Tests:** 76/76 auxiliary client tests passing. 25 pre-existing failures in full suite (redact test ordering issue, present on clean main).

Credit: @0xbyt4 (original author, commit authorship preserved).