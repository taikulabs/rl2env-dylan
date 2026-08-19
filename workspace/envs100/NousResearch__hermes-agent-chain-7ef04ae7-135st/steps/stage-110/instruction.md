**fix(agent): repair empty-name tool_calls in sanitizer to prevent Responses 400 (salvage #12807/#52893)**

## Summary

Empty-name `tool_call`s in conversation history no longer brick a session with HTTP 400 — the pre-call sanitizer now repairs them instead of letting them produce an orphan output downstream.

Salvage of #12807 (idea by @melonboy312) via @Bartok9's rebased commits. Supersedes #11435 (@ygd58), which fixed the same 400 but in the wrong place and by dropping the orphan output — which would strip the intentional anti-priming signal (see below).

## Root cause

A stored `assistant` `tool_call` with an `id` but an empty/missing `function.name` (from partial streaming or certain providers) survives `sanitize_api_messages` untouched. The Responses-API serializer (`_chat_messages_to_responses_input`) then **drops** the nameless `function_call` while still emitting its paired `function_call_output`. The orphan output makes the provider reconstruct the name as an empty string and reject the whole request:

```
HTTP 400: Invalid 'input[n].name': empty string.
```

`sanitize_api_messages` already repaired orphan tool_call/result *pairs*, but never the empty-*name* case itself.

## Fix

Add a repair pass in `sanitize_api_messages` (runs unconditionally before **every** LLM call — chat-completions and Responses alike): rename any blank `function.name` to a non-empty sentinel (`invalid_tool_call`) so the call and its result stay **paired**. The serializer no longer drops the `function_call`, so there is no orphan output and no 400.

**Why rename, not drop:** hermes' dispatch loop intentionally keeps an empty-name call paired with a synthesized anti-priming `"tool name was empty"` result so weak models self-correct instead of being fed the full tool catalog. Dropping the call (the #11435 approach) would orphan that result and strip the anti-priming signal. Renaming preserves it.

## Changes

- `agent/agent_runtime_helpers.py`: Pass-0 empty-name repair in `sanitize_api_messages` before the orphan-pairing logic.
- `tests/run_agent/test_run_agent.py`: regression test — empty-name call is renamed (not dropped), its result survives, no orphan.

## Validation

| | Before | After |
|---|---|---|
| Empty-name `tool_call` in history | orphan `function_call_output` → HTTP 400 | renamed → paired `function_call` emitted, no 400 |
| Anti-priming `"tool name was empty"` result | dropped by #11435 approach | preserved |
| Targeted tests | — | 8/8 pass |

E2E (real `sanitize_api_messages` → `_chat_messages_to_responses_input`): the standalone orphan that triggers the 400 is gone, the anti-priming result is preserved, and every emitted `function_call` has a non-empty name.

.

## Infographic

![fix infographic](https://v3b.fal.media/files/b/0aa06d49/n9XxQilbr4ISgHPHzPf2j_WcmCCWzb.png)

---
Nous Research