**feat(gateway): cache AIAgent per session for prompt caching**

## Problem

The gateway created a fresh `AIAgent` per message, rebuilding the system prompt (including memory, skills, context files) every turn. This broke prompt prefix caching — providers like Anthropic charge ~10x more for uncached prefixes ($3/MTok vs $0.30/MTok).

CLI didn't have this problem because it reuses a single `AIAgent` across all turns with `_cached_system_prompt` built once.

## Fix

Cache `AIAgent` instances per `session_key` with a config signature. The cached agent is reused across messages in the same session, preserving the frozen system prompt and tool schemas.

**Cache invalidation:**
- Config changes (model, provider, toolsets, reasoning, ephemeral prompt) — automatic via signature mismatch
- `/new`, `/reset`, `/clear` — evicts session's cached agent
- `/model` — clears all cached agents (global config change)
- `/reasoning` — clears all cached agents

**Per-message state** (callbacks, stream consumers, progress queues) is set on the agent instance before each `run_conversation()` call — these are not cached.

## What stays frozen (cached across turns)

- `_cached_system_prompt` — system prompt with memory, skills, context files
- `self.tools` — tool schemas resolved in `__init__`
- Model, provider, base_url — all config that affects the API call shape

## What's fresh each turn

- Conversation history (from session transcript)
- Callbacks (progress, streaming, hooks)
- Honcho context
- Todo store hydration

5753 tests passing (1286 gateway tests).