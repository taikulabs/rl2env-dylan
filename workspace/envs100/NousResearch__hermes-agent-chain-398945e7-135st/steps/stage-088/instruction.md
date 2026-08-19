**fix(tools): dedup tool names at API boundary for Vertex/Azure/Bedrock (salvage #18532)**

Providers that enforce tool-name uniqueness (Google Vertex, Azure, Amazon Bedrock, Anthropic) now receive deduplicated tool lists even if an upstream injection path regresses. Before this change, a duplicate from any source (context-engine plugin re-registration, cache poisoning, re-init path) caused HTTP 400 `Tool names must be unique` — non-retryable and silent when fallback chains exhausted.

## What changed
- `agent/auxiliary_client.py`: `_build_call_kwargs()` dedups tools before `kwargs["tools"] = …` (covers all chat_completions providers).
- `agent/anthropic_adapter.py`: `convert_tools_to_anthropic()` dedups in the loop (covers the native Anthropic Messages API path).
- Dupes are dropped with `logger.warning`, first occurrence wins.
- 8 new tests (4 per module) cover unique passthrough, dedup, empty, None.

## Why this layer (and not just the root-cause fix)
The root-cause dedup in `run_agent.py` (context-engine + memory-tool injection) is already on main — this PR adds defensive guards at the two API-boundary functions so any future injection-path regression converts a hard 400 into a warning rather than silently exhausting the fallback chain. Intentionally conservative.

## Validation
- `scripts/run_tests.sh tests/agent/test_auxiliary_client.py tests/agent/test_anthropic_adapter.py` → 260 passed.
- E2E: real `_build_call_kwargs(provider="openrouter", …)` and `convert_tools_to_anthropic(…)` called with a 7-tool list containing 2 duplicates (simulating the hermes-lcm plugin double-registration). Both paths return 5 unique tools, first-occurrence ordering preserved.

.