**fix(transport): omit thinking_config for Gemma on the gemini provider**

Salvage of #17441 by @briandevans onto current main.

## Summary
On the `gemini` provider, omit `thinking_config` from the request whenever the model isn't actually Gemini (Gemma, PaLM, etc.). The Gemini API rejects unknown field names with HTTP 400 — including the polite `{"includeThoughts": False}` shape — so the field must be absent entirely, not merely disabled.

Regression from the 2026.4.23 release (thinking_config bridging): Gemma users on the `gemini` provider got `HTTP 400: Unknown name "thinking_config": Cannot find field` on every chat and exited immediately.

## Changes
- `agent/transports/chat_completions.py`: move model-family detection into `_build_gemini_thinking_config()` — normalize model id, strip OpenRouter-style `google/` prefix, return `None` when the result doesn't start with `gemini`. Covers all three call sites (native gemini, OpenAI-compat nested-under-`google`, google-gemini-cli) since they all funnel through this helper.
- `tests/agent/transports/test_chat_completions.py`: +3 regression cases (gemma enabled, gemma disabled, `google/`-prefixed gemma).

## Validation
`scripts/run_tests.sh tests/agent/transports/test_chat_completions.py` → **59 passed** (56 existing Gemini cases unchanged, 3 new Gemma cases green).

.
.