**fix(agent): persist streamed reasoning_content on assistant turns**

Supersedes #16884 with a scoped rework that preserves existing read-side compensation.

## Summary
Streaming-only providers (glm, MiniMax, gpt-5.x via aigw, Anthropic via openai-compat shims) accumulate reasoning through `delta.reasoning_content` chunks but never expose it as a top-level attribute on the finalized SDK message. The existing `hasattr`-guarded block at `_build_assistant_message` therefore never wrote `reasoning_content` for those providers, so the chain-of-thought was persisted only under the internal `reasoning` key.

The poison is silent until the user later switches to a DeepSeek-v4 or Kimi thinking model, at which point replay 400s with "The reasoning_content in the thinking mode must be passed back to the API." Issue #16844 reports 4,031 poisoned messages across 1,101 session files on one install.

## Changes
- `run_agent.py` `_build_assistant_message`: additive fallback promotes the already-sanitized `reasoning_text` to `reasoning_content` when no earlier branch wrote it and reasoning text was actually captured. Existing SDK-attr branch and DeepSeek `""`-pad are untouched.
- `tests/run_agent/test_run_agent.py`: 3 regression tests — streaming promotion path, SDK precedence, field-absent-when-no-reasoning invariant.

## Why not #16884 as-written
#16884 replaced the conditional with `msg["reasoning_content"] = ""` as a universal fallback, which would have:
1. Triggered the Anthropic adapter's `isinstance(reasoning_content, str)` branch to prepend an empty `{"type":"thinking","thinking":""}` block on every replayed assistant turn.
2. Sent `reasoning_content: ""` to every strict OpenAI-compatible provider (Mistral, Fireworks, stock OpenAI, GitHub Models).
3. Short-circuited `_copy_reasoning_content_for_api`'s step-1 string check on every turn, making tiers 2–4 dead code — including #15748's cross-provider reasoning-leak guard for DeepSeek/Kimi.

The layered approach here solves the write-side bug without changing the field's presence semantics for non-thinking sessions. Existing read-side ladder (cross-provider leak guard #15748, promote-from-`reasoning`, DeepSeek/Kimi thinking-pad) stays live as defense in depth.

## Validation
| | Before | After |
|---|---|---|
| Streaming reasoning persisted (glm, MiniMax, gpt-5.x via aigw) | missing `reasoning_content` → 400 on DeepSeek/Kimi replay | promoted at write time |
| SDK-exposed `reasoning_content` | preserved | preserved |
| DeepSeek tool-call `""`-pad | fires | fires |
| Non-thinking turns (no reasoning) | field absent | field absent |
| `_copy_reasoning_content_for_api` tiers 2–4 | live | live |
| #15748 cross-provider leak guard | live | live |
| Targeted tests: `TestBuildAssistantMessage` + `test_deepseek_reasoning_content_echo` | n/a | 15 + 23 passing |

Credit @Sanjays2402 for the original diagnosis in #16884.

, #16884, #15250, #15353, #15748.