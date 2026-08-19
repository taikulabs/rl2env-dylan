**fix(bedrock): send context-1m-2025-08-07 beta so Opus 4.6/4.7 get 1M context**

## Summary
Bedrock Claude Opus 4.6/4.7 and Sonnet 4.6 now get the full 1M context window. Previously Hermes advertised 1M in `model_metadata.py` but sent requests without the beta header Bedrock requires, silently capping output at 200K.

## Root cause
On AWS Bedrock (and Azure AI Foundry), the 1M window is still gated behind the `context-1m-2025-08-07` anthropic-beta header as of 2026-04. On native Anthropic it went GA, so the header is a harmless no-op there. Hermes never sent the header anywhere — Bedrock users hit the 200K cap with no error, Claude Code using the same Bedrock credentials worked because it sends the header by default.

Reported on Discord by user 'Rodmar' — Opus 4.7 on Bedrock limited to 200K; region swap, global prefix, `[1m]` model suffix all no-ops (Hermes has no code paths for any of those).

## Changes
- `agent/anthropic_adapter.py`: add `context-1m-2025-08-07` to `_COMMON_BETAS`.
- `agent/anthropic_adapter.py`: strip the 1M beta in `_common_betas_for_base_url` for MiniMax bearer-auth endpoints (they don't host Claude; unknown Anthropic betas could risk rejection).
- `agent/anthropic_adapter.py`: attach `_COMMON_BETAS` as `default_headers` on the `AnthropicBedrock` client — previously the constructor passed no betas at all.
- `tests/agent/test_bedrock_1m_context.py`: 5 new tests covering native/Bedrock/MiniMax paths and the fast-mode `extra_headers` override.

Fast-mode per-request `extra_headers` already rebuilds from `_common_betas_for_base_url`, so it picks up the 1M beta automatically — verified by test.

## Validation
| | Before | After |
|---|---|---|
| `_COMMON_BETAS` | 2 entries | 3 entries (+ context-1m-2025-08-07) |
| Bedrock client `default_headers` | (none) | `anthropic-beta: interleaved-thinking, fine-grained-tool-streaming, context-1m-2025-08-07` |
| MiniMax bearer endpoint betas | strips 1 | strips 2 (tool-streaming + 1M) |
| Opus 4.7 effective Bedrock context | 200K | 1M |
| New tests | — | 5/5 pass |
| Existing `test_minimax_provider.py` | 41/41 | 41/41 |