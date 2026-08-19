**fix(agent): drop thinking-only assistant turns before provider call**

## Summary
Adds a pre-call sanitizer that detects assistant turns containing only reasoning (no visible content, no tool_calls) and drops them from the wire copy. Adjacent user messages left behind are merged so role alternation stays intact.

Mirrors Claude Code's `filterOrphanedThinkingOnlyMessages` + `mergeAdjacentUserMessages` pattern (src/utils/messages.ts). Chosen after comparing against three contributor PRs (#11098, #13010, #16842) that tried to fix the same 400 class by fabricating stub text (`.` / `(continued)`) — which puts words in the model's mouth. Dropping the turn is honest; merging preserves the provider's invariant.

## Changes
- `run_agent.py`: +`_is_thinking_only_assistant()` detector, +`_drop_thinking_only_and_merge_users()` pass; wired in after `_sanitize_api_messages` in the main loop and in the iteration-limit-summary retry path
- `tests/run_agent/test_thinking_only_sanitizer.py`: 25 unit tests

The stored conversation history (`self.messages`) is never mutated — only the per-call `api_messages` copy. Users still see the reasoning block in CLI/gateway transcripts; session persistence keeps the full trace.

## Validation

**Unit tests**
```
tests/run_agent/test_thinking_only_sanitizer.py: 25 passed
tests/run_agent/ + tests/agent/test_anthropic_adapter.py: 1290 passed (2 pre-existing failures on main, unrelated)
```

**Live E2E (`poisoned history → clean response`), 5 providers**

| Provider (via) | Poisoned history | Happy path |
|---|---|---|
| OpenRouter → Anthropic claude-sonnet-4.6 | ✓ 'Hello! Blue.' | ✓ '4' |
| OpenRouter → OpenAI gpt-5 | ✓ 'Hi.\\n\\nBlue.' | ✓ '4' |
| OpenRouter → DeepSeek R1 | ✓ 'Hello.\\n\\nBlue.' | ✓ '4' |
| OpenRouter → Qwen3-Max | ✓ 'Hello!\\n\\nBlue.' | ✓ '4' |
| Native Gemini 2.5-flash | ✓ 'Hello!\\n\\nBlue.' | ✓ '4' |

Poisoned history = `[user(A), assistant(empty + reasoning_content), user(B)]`. Sanitizer drops the assistant turn and merges users → `[user(A + B)]`. Verified via trace: 4 input messages → 2 output messages, and the merged content contains both original user texts concatenated with `\\n\\n`. Happy path verifies it's a noop when no thinking-only turn exists.

## Related
- #16823 (wontfix) — the stub-text approach these PRs tried
- , #13010, #16842 — all three fabricated text; this PR implements the alternative