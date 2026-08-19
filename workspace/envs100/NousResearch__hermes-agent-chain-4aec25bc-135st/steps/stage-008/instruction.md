**feat(x_search): gated X (Twitter) search tool with OAuth-or-API-key auth**

## Summary

Brings back the X (Twitter) search tool we removed from PR #10786, gated so it only registers when the user has xAI credentials — **either** a paid \`XAI_API_KEY\` **or** a SuperGrok OAuth login.

Both paths route to xAI's built-in \`x_search\` Responses tool at \`https://api.x.ai/v1/responses\`. When both credentials exist OAuth wins, matching \`tools/xai_http.py\`'s existing preference order (uses SuperGrok subscription quota instead of paid API spend).

## How the gating works

\`check_x_search_requirements()\` calls \`tools.xai_http.resolve_xai_http_credentials()\`, which:

1. Tries the xai-oauth runtime provider (refreshes OAuth bearer if expiring)
2. Falls back to the direct OAuth resolver
3. Falls back to \`XAI_API_KEY\` (read from \`~/.hermes/.env\` first, then env)

A \`True\` return means the bearer is fetchable AND non-empty. The check_fn result is TTL-cached by the registry. Resolver exceptions (revoked token + failed refresh) gate the tool out cleanly.

Off by default — users opt in via \`hermes tools\` → 🐦 X (Twitter) Search. The tool's check_fn means the schema stays hidden from the model when no xAI credentials exist regardless of toolset enablement.

## Changes

| File | LOC | What |
|------|-----|------|
| \`tools/x_search_tool.py\` | +370 (new) | Salvaged from #10786, credential resolution reworked to use \`resolve_xai_http_credentials()\`. Bearer resolved per-call so revoked OAuth surfaces a tool_error instead of an HTTP 401. |
| \`toolsets.py\` | +11 | \`x_search\` toolset def. NOT added to \`_HERMES_CORE_TOOLS\` — opt-in. |
| \`hermes_cli/tools_config.py\` | +41 | \`CONFIGURABLE_TOOLSETS\` row + \`TOOL_CATEGORIES[\"x_search\"]\` with two provider options (OAuth + API key) sharing the existing \`xai_grok\` post_setup hook. |
| \`hermes_cli/config.py\` | +17 | \`DEFAULT_CONFIG[\"x_search\"]\` (model, timeout_seconds, retries). Additive nested key; no version bump. |
| \`tests/tools/test_x_search_tool.py\` | +414 (new) | 13 tests: HTTP shape, handle filter validation, citation extraction, 4xx/5xx/timeout retries, full credential matrix (OAuth-only, API-key-only, both-set, none-set, resolver-raises, config overrides, registry registration). |
| \`website/docs/guides/xai-grok-oauth.md\` | +6 | X Search added to the direct-to-xAI tools section with off-by-default note. |
| \`website/docs/user-guide/features/tools.md\` | +1 | New row in the tools table. |

## Validation

| | Result |
|---|---|
| \`tests/tools/test_x_search_tool.py\` | 13/13 passed (0.4s) |
| \`tests/tools/\` + \`tests/hermes_cli/test_tools_config.py\` + \`tests/test_toolsets.py\` | 106/106 passed (1.2s) |
| Related xai_http tests (TTS, transcription, video_gen plugin) | 119/119 passed (1.5s) |
| E2E gating (no creds → schema hidden; API key → registered; OAuth → registered) | Verified with isolated HERMES_HOME |

## Credit

Original X search implementation from @Jaaneek in PR #10600 / salvage PR #10786. The tool body, schema, retry logic, citation extraction, and HTTP shape are theirs — credential resolution and gating are new.

Co-authored-by: Jaaneek <Jaaneek@users.noreply.github.com>