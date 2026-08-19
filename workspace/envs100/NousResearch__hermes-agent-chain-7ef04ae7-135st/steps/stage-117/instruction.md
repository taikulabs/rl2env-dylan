**fix(anthropic+feishu): model-gate max_tokens fallback; wire Feishu channel_prompt**

## Summary
Two independent fixes salvaged from #12811 (now closed — its third bundled fix, Discord `free_response_channels`, is already on `main`).

**Anthropic `max_tokens`:** Claude models served over any chat-completions proxy now get a `max_tokens` fallback, not just OpenRouter/Nous.

**Feishu `channel_prompt`:** Feishu now honours `channel_prompts` config like Discord and Slack.

## Changes
- `agent/chat_completion_helpers.py`: the `max_tokens` fallback gate in `build_api_kwargs` changes from **URL-gated** (`OpenRouter || Nous`) to **model-gated** (`model ∈ _ANTHROPIC_OUTPUT_LIMITS`). Any proxy serving Claude/MiniMax/Qwen3 (AWS Bedrock, NVIDIA, LiteLLM, vLLM, corporate gateways) now gets the model's native output limit. Stays a last-resort fallback — `build_kwargs` applies it only after ephemeral/user/profile `max_tokens`, so it never overrides an explicit value, and only the chat-completions transport is touched (native Anthropic Messages API is a separate path).
- `plugins/platforms/feishu/adapter.py`: added `_resolve_channel_prompt()` (delegating to shared `gateway.platforms.base.resolve_channel_prompt`), wired into all three `MessageEvent` sites — inbound message, reaction routing, card-action routing.
- `tests/gateway/test_feishu_channel_prompts.py`: 6 new cases.

## Root cause
- #12790: Bedrock and other proxies default to ~4096 output tokens; with no `max_tokens` sent, the model exhausts its budget on thinking + large tool calls (`write_file`, `patch`). The old `"claude" in model` substring gate also silently skipped MiniMax/Qwen3 entries in the limits table — fixed as a side effect.
- #12805: the Feishu adapter never called any channel-prompt resolver, so `channel_prompts` config was silently ignored.

## Validation
| | Before | After |
|---|---|---|
| Claude on Bedrock/LiteLLM/vLLM | no `max_tokens` → proxy default (4096) | native limit (e.g. 64000) |
| MiniMax / Qwen3 on any proxy | missed by gate | covered |
| Explicit user `max_tokens` | honoured | honoured (fallback never overrides) |
| Feishu `channel_prompts` | ignored | resolved + attached to event |
| Targeted tests | — | 346 pass (6 new Feishu cases), ruff clean |

, #12805. Credit to @vominh1919 for reporting all three and the original bundled fix.

## Infographic
![PR infographic](https://v3b.fal.media/files/b/0aa06f11/cjLTW5zi7XrnbId-qqxlI_q0xFzNxR.png)