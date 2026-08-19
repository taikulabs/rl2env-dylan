**fix: keep plain custom GPT-5 relays on chat completions (salvage #11436)**

## Summary
Plain `provider: custom` GPT-5 relays now stay on chat completions instead of being force-upgraded to the OpenAI Responses API. Salvage of #11436 by @HiddenPuppy onto current main.

## Root cause
Hermes treated `gpt-5*` as sufficient to force the Responses API even for generic custom relays, and it respected a stale persisted `model.api_mode=codex_responses` for plain custom endpoints. Some OpenAI-compatible relays don't implement Responses semantics, which surfaced as malformed `function_call.name` replay errors in gateway sessions.

## Changes
- `hermes_cli/runtime_provider.py`: custom-provider `api_mode` now routes through new `_resolve_plain_custom_api_mode()`, which drops a stale `codex_responses` unless the URL is direct OpenAI/xAI.
- `run_agent.py`: `_provider_model_requires_responses_api()` returns `False` for `provider=custom`. Direct `api.openai.com` / `api.x.ai` custom URLs still upgrade because `_is_direct_openai_url()` / URL detection is checked first.
- Regression coverage for plain relays vs direct OpenAI/xAI URLs (runtime_provider + AIAgent init paths).

## Validation
| Case | api_mode |
|---|---|
| custom relay + stale `codex_responses` | `chat_completions` |
| custom @ `api.openai.com` + `codex_responses` | `codex_responses` (preserved) |
| custom relay + `anthropic_messages` | `anthropic_messages` (preserved) |

- `scripts/run_tests.sh tests/run_agent/test_run_agent_codex_responses.py -k custom_provider` — 2 passed
- `scripts/run_tests.sh tests/hermes_cli/test_runtime_provider_resolution.py -k '...'` — 4 passed
- E2E: real `resolve_runtime_provider()` against isolated `HERMES_HOME`, all 3 cases pass.

## Infographic
![infographic](https://v3b.fal.media/files/b/0aa06d55/VUT5-3B50uYqOdHTmNEFZ_TKVOL6Dl.png)