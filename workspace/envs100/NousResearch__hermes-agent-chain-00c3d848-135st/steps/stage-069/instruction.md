**fix(agent): block cross-provider reasoning leak to DeepSeek/Kimi**

## Summary
Cross-provider session switches (e.g. MiniMax → DeepSeek) no longer leak the prior provider's chain of thought into DeepSeek's `reasoning_content` — .

Root cause: `_copy_reasoning_content_for_api` promoted any `reasoning` field to `reasoning_content` before the DeepSeek/Kimi empty-pad check. When the source turn came from a different provider (no `reasoning_content` key, `reasoning` set by the prior provider), the foreign chain of thought was sent to DeepSeek on replay.

## Changes
- `run_agent.py::_copy_reasoning_content_for_api`: new step 2 — when on DeepSeek/Kimi AND the source turn has `tool_calls` AND `reasoning` is set AND `reasoning_content` key is absent, inject `""` instead of promoting `reasoning`. Rationale: `_build_assistant_message` always pins `reasoning_content=""` for same-provider DeepSeek tool-call turns, so that shape is unreachable from same-provider history.
- Tests: update `test_deepseek_reasoning_field_promoted` to exercise the reachable same-provider shape (no `tool_calls`), add `test_deepseek_poisoned_cross_provider_history_padded` + `test_kimi_poisoned_cross_provider_history_padded` for the #15748 scenario.

## Validation
| scenario | before | after |
|---|---|---|
| #15748 MiniMax reasoning → DeepSeek tool-call replay | `'MiniMax thinking...'` | `""` |
| same-provider DeepSeek text turn w/ reasoning | promoted | promoted (unchanged) |
| explicit `reasoning_content` set (incl. `""` placeholder) | preserved | preserved (unchanged) |
| non-DeepSeek provider (e.g. OpenAI) | untouched | untouched (unchanged) |

Test results: `tests/run_agent/test_deepseek_reasoning_content_echo.py` — 23 passed (21 existing + 2 new).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_deepseek_reasoning_content_echo.py`