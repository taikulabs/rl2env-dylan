**feat(grok): apply OpenAI execution guidance to xAI Grok / xai-oauth models**

## Summary
xAI Grok models (xai-oauth + OpenRouter grok-*) now get the same family-specific execution discipline block (`OPENAI_MODEL_EXECUTION_GUIDANCE`) that GPT/Codex get. Same failure modes in practice: claims completion without tool calls ("to be honest, I didn't create the file yet"), suggests workarounds instead of using existing tools (proposing a folder-based memory system when the memory tool exists), replies with plans instead of executing.

The base `TOOL_USE_ENFORCEMENT_GUIDANCE` was already firing for grok ("grok" is in `TOOL_USE_ENFORCEMENT_MODELS`). This was just the family-specific second tier that GPT/Codex got and Grok didn't.

## Changes
- `agent/system_prompt.py`: gate at L159 also matches `"grok" in _model_lower`
- `agent/prompt_builder.py`: docstring note that `OPENAI_` prefix reflects origin, not exclusivity (body is family-agnostic — tool_persistence / mandatory_tool_use / act_dont_ask / prerequisite_checks / verification / missing_context)
- `tests/run_agent/test_run_agent.py`: 4 new tests covering OpenRouter slug, xai-oauth bare name, and a claude negative control

## Validation
| | Before | After |
|---|---|---|
| Grok base enforcement block | injected | injected |
| Grok exec discipline (verification, mandatory_tool_use, act_dont_ask) | **missing** | **injected** |
| Claude exec discipline | not injected | not injected |

- `TestToolUseEnforcementConfig`: 16/16 pass (12 pre-existing + 4 new)
- `test_prompt_builder.py`: 122/122 pass
- E2E with real `AIAgent._build_system_prompt()`: `grok-4.3` (xai-oauth) and `x-ai/grok-4.20` (openrouter) both inject the full block including `<verification>`, `<mandatory_tool_use>`, `<act_dont_ask>`; `claude-sonnet-4` does not.