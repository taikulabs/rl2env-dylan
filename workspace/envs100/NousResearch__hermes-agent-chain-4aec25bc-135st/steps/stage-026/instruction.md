**fix(xai): surface provider 'error' SSE frame in Codex fallback stream**

## Summary
Grok 4.3 / 4.20 no longer fail with bare RuntimeError — accounts that hit a subscription, quota, or reasoning-replay rejection now see the real xAI message once instead of three retries of \`RuntimeError: Responses create(stream=True) fallback did not emit a terminal response.\`

Root cause: xAI emits \`type=error\` as the first Responses SSE frame for these accounts (May 2026 SuperGrok rollout). The SDK helper raises \`RuntimeError(Expected to have received response.created before error)\`, which is correctly caught and routed to \`_run_codex_create_stream_fallback\`. That fallback opens a new stream, xAI emits the same \`error\` frame again, but the fallback loop only watched for \`{response.completed, response.incomplete, response.failed}\` and silently \`continue\`d past \`error\` events — falling off the end of the stream and raising the unhelpful terminal error.

Reported by community user (Sic): https://paste.rs/OQyYj

## Changes
- \`run_agent.py\`: new \`_StreamErrorEvent\` exception with OpenAI SDK-shaped \`.body = {\"error\": {...}}\` so \`_summarize_api_error\`, \`_extract_api_error_context\`, \`_is_entitlement_failure\`, and \`classify_api_error\` all see the real provider message.
- \`run_agent.py\`: \`_run_codex_create_stream_fallback\` now raises \`_StreamErrorEvent\` when it encounters a \`type=error\` SSE event (both attribute-style and dict-style payloads).
- \`tests/run_agent/test_streaming.py\`: 4 new tests in \`TestCodexFallbackErrorEvent\`.

## Validation

| Path | Before | After |
|---|---|---|
| User-facing error | \`RuntimeError: ...did not emit a terminal response.\` ×3 retries | \`...do not have an active Grok subscription.\` ×1, no retry |
| \`_summarize_api_error\` | \"RuntimeError\" | full xAI message |
| \`classify_api_error\` | \`unknown / retryable=True\` | \`auth / retryable=False\` |
| \`_is_entitlement_failure\` | never reached | matches even with \`status_code=None\` |

End-to-end verified via direct invocation of the classifier and summarizer on a synthesized \`_StreamErrorEvent\` carrying xAI's real subscription message.

Tests: \`scripts/run_tests.sh tests/run_agent/test_streaming.py tests/run_agent/test_codex_xai_oauth_recovery.py\` → 62 passed.

## Caveat
This fix doesn't make Grok start working for users who actually lack a SuperGrok subscription — it just makes the failure message accurate. For users who have a subscription and are still hitting this, they'll now see whatever xAI's real message is.