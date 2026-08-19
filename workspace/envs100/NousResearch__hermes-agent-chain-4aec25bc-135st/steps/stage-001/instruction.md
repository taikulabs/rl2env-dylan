**fix(xai-oauth): recover from prelude SSE errors, gate reasoning replay, surface entitlement 403s**

## Summary
Three fixes for the multi-turn / 403 failures reported on the May 2026 xAI OAuth (SuperGrok / X Premium) rollout. Each is independently useful; together they make xai-oauth chat work end-to-end on a subscribed account and produce an actionable error on an unsubscribed one.

## Changes
- `run_agent.py::_run_codex_stream` — when the OpenAI SDK raises `RuntimeError("Expected to have received \`response.created\` before \`<type>\`")`, retry once then fall back to `responses.create(stream=True)` (same path we already use for the missing-`response.completed` postlude). The fallback surfaces the real provider error as a normal exception with body+status_code attached. Also  (`response.in_progress` prelude on custom relays) and #14634 (`codex.rate_limits` prelude on codex-lb).
- `run_agent.py::_summarize_api_error` — when an error body matches xAI's entitlement shape ("do not have an active Grok subscription" / "out of available resources" + "grok"), append `— xAI OAuth account lacks SuperGrok / X Premium entitlement for this model. Subscribe at https://grok.com or run /model to switch providers.` Once-only, applies to both auxiliary warnings and main-loop error messages.
- `agent/codex_responses_adapter.py` + `agent/transports/codex.py` — new `is_xai_responses` kwarg on `_chat_messages_to_responses_input` drops replayed `codex_reasoning_items` (with `encrypted_content`) before they're sent to xAI. Also drops `reasoning.encrypted_content` from the xAI `include` array since we no longer replay it. Native Codex (`openai-codex`) behavior is unchanged. Grok still reasons natively each turn; coherence across turns rides on visible message text.

## Validation
| | Result |
|---|---|
| New targeted tests (`test_codex_xai_oauth_recovery.py`) | 15/15 pass |
| `tests/run_agent/` + `test_auth_xai_oauth_provider.py` | 1426 passed, 3 skipped, 0 failures |
| `tests/agent/transports/` + aux client + title generator | 339/339 pass |
| E2E (real imports, isolated HERMES_HOME) | prelude fallback / entitlement hint / replay gating all green |

## Closes
- #8133
- #14634