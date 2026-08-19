**fix(delegation): honor api_mode + auto-detect anthropic_messages URLs**

Salvages #10273 (HiddenPuppy) — preserves attribution via Co-Authored-By.

## Summary
Subagent delegation now picks anthropic_messages automatically for direct base URLs ending in /anthropic (Azure AI Foundry, MiniMax, Zhipu GLM, LiteLLM proxies, …) and honors an explicit delegation.api_mode when the URL heuristic can't classify the endpoint.

.

## Root cause
tools/delegate_tool.py::_resolve_delegation_credentials hardcoded `api_mode = "chat_completions"` for any delegation.base_url not matching three specific hostnames (chatgpt.com/backend-api/codex, api.anthropic.com, api.kimi.com/coding) and never read delegation.api_mode from config. Foundry's https://foundry.services.ai.azure.com/anthropic fell through, got chat_completions, hit Foundry's Anthropic path with OpenAI-shaped requests → 404. The main agent works because it routes through the shared _detect_api_mode_for_url() helper (anything ending in /anthropic → anthropic_messages); delegation reimplemented its own narrower check.

## Changes
- tools/delegate_tool.py: reuse _detect_api_mode_for_url() and honor explicit delegation.api_mode; keep existing Codex/native-Anthropic/Kimi-coding hostname overrides
- hermes_cli/config.py: document the new delegation.api_mode key
- tests/tools/test_delegate.py: 4 regression tests covering auto-detection of /anthropic suffix, explicit override, override-wins-over-detection, and invalid-value fallback

## Validation
| | Before | After |
|---|---|---|
| Foundry /anthropic URL, no api_mode | chat_completions (404) | anthropic_messages |
| Foundry /anthropic URL, api_mode: anthropic_messages | chat_completions (404) | anthropic_messages |
| localhost OpenAI-compat (regression) | chat_completions | chat_completions |
| Native api.anthropic.com (regression) | anthropic / anthropic_messages | anthropic / anthropic_messages |
| chatgpt.com/backend-api/codex (regression) | openai-codex / codex_responses | openai-codex / codex_responses |

- tests/tools/test_delegate.py::TestDelegationCredentialResolution → 12/12
- tests/tools/test_delegate.py → 131/131
- Live E2E with real imports against the user's exact reported config: anthropic_messages resolved correctly