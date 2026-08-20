**fix(moa): forward slot api_mode + pin chat_completions on live MoA switch**

## Summary
Two Mixture-of-Agents transport bugs that broke reference and primary calls are now fixed: MoA slots route through their resolved `api_mode`, and a live switch to a MoA preset always speaks `chat_completions` on the primary call.

## Changes
- `agent/moa_loop.py` + `agent/auxiliary_client.py`: `_slot_runtime` now forwards the resolved `api_mode`, and `call_llm` accepts an `api_mode` override (
- `agent/agent_runtime_helpers.py`: `switch_model` now pins `api_mode = "chat_completions"` in the `provider == "moa"` branch, mirroring `agent_init.py`. The aggregator's real transport is resolved *inside* the reference/aggregator fan-out, never on the outer primary call.
- Tests: salvaged `test_moa_slot_api_mode.py`; added `test_moa_switch_api_mode.py` asserting the pin holds across `codex_responses`/`anthropic_messages`/`chat_completions`/empty incoming modes.

## Root cause
- **Bug 1 (#54379, #55268):** `_slot_runtime` resolved each slot's `api_mode` but forwarded only `base_url` + `api_key`. The URL heuristic can't recover the transport for Copilot Responses models or anthropic-wire hosts off `api.anthropic.com`, so those slots used the wrong endpoint.
- **Bug 2 (#54259, #54669):** the live `/model` switch built the `MoAClient` facade but left `agent.api_mode` at the aggregator's transport. The conversation loop dispatched `client.responses.create` (MoAClient has no `.responses`), fell through to the `moa://local` placeholder → 404 → fallback to a reference model. The `/moa` one-shot path already pinned `chat_completions`, which is why one-shot worked but persisted presets didn't.

## Validation
| | Before | After |
|---|---|---|
| Copilot GPT-5.x reference | 400 `unsupported_api_for_model` | routed via `codex_responses` |
| anthropic_messages aggregator (unknown host) | 404 | routed via `anthropic_messages` |
| Live switch to MoA preset (gateway) | primary call → `moa://local` 404 → fallback | `MoAClient.chat.completions` |
| `test_moa_slot_api_mode` / `test_moa_switch_api_mode` / `test_moa_loop_mode` | — | 25 passed, 0 failed |

, #55268, #54259, #54669.

## Infographic
![MoA wire-routing fixes](https://v3b.fal.media/files/b/0aa05c18/and-yNHvVmi0HbjRxrD_T_hywYgVjJ.png)

---
Nous Research

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_moa_switch_api_mode.py`