**fix(agent): preserve reasoning_content replay on DeepSeek v4 + Kimi/Moonshot thinking**

## Summary
DeepSeek v4 thinking mode (and Kimi / Moonshot thinking) stop 400'ing on multi-turn tool-call replays with "The reasoning_content in the thinking mode must be passed back to the API." .

## Root cause
`run_agent.py::_build_assistant_message` had a pad branch guarded by `msg.get("tool_calls")`, which was always falsy because `tool_calls` were assigned ~60 lines later in the same method. When DeepSeek returned `reasoning_content=None` on a tool-call turn and streaming captured no thinking text, the turn was persisted bare; the next replay hit the 400. Same enforcement exists on Kimi / Moonshot, reachable through the same code path. A secondary hole: when the OpenAI SDK doesn't know a provider's schema (aggregator passthrough like OpenCode Go → DeepSeek), `reasoning_content` lands in `model.model_extra` instead of a typed attribute and the builder never sees it.

## Changes
Salvages two open PRs:

- **#16855** (@lsdsjy): captures `assistant_tool_calls` at method entry so the pad check reads the SDK source of truth, falls back to `model.model_extra["reasoning_content"]` when the typed attr is absent (covers aggregator paths like OpenCode Go), and mirrors the `model_extra` fallback in the `chat_completions` transport normalizer. Uses `reasoning_text or ""` so captured streaming reasoning is preserved when padding.
- **#17489** (@season179): extends the pad to Kimi / Moonshot via a shared `_needs_thinking_reasoning_pad()` helper that's reused in `_copy_reasoning_content_for_api` (dedupes the `deepseek or kimi` predicate across both sites).

Follow-ups added here:
- `scripts/release.py`: AUTHOR_MAP entries for `lsdsjy` and `season179`.
- Test helpers (`_ATTR_ABSENT`, `_EXPECT_NOT_PRESENT`, `_sdk_tool_call`, `_build_sdk_message`) from #17489 added alongside #16855's `TestBuildAssistantMessageDeepSeekReasoningContent`.

. . .

## Validation

| | Targeted tests | Run on |
|---|---|---|
| Before fix (stash run_agent.py) | 2 Kimi/Moonshot parametrized cases FAIL | `test_deepseek_reasoning_content_echo.py` |
| After fix | 34 pass | `test_deepseek_reasoning_content_echo.py` |
| After fix | 95 pass | `test_deepseek_reasoning_content_echo.py` + `test_chat_completions.py` |
| Wider sweep | 1339 passed, 17 skipped | `tests/run_agent/ tests/agent/transports/` |

The targeted empirical check (stash + rerun) proves the new Kimi/Moonshot cases exercise the extension on top of #16855, not trivially pass. The 3 DeepSeek parametrized cases pass in both scenarios because they were already fixed by the #16855 cherry-pick.

## Credits
- @lsdsjy — original DeepSeek v4 + model_extra fix
- @season179 — Kimi/Moonshot extension, shared predicate

Co-authored-by: lsdsjy <luwinyang@deepseek.com>
Co-authored-by: season179 <season.saw@gmail.com>