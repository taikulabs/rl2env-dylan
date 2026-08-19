**fix(agent): flatten multi-part user_message in codex intermediate-ack detector**

## Summary
Vision requests no longer crash the codex intermediate-ack detector. The OpenAI-compat API server forwards a multi-part content list as `user_message`; the detector flattened it with `(user_message or "").strip()`, so a truthy list survived and `.strip()` raised `AttributeError`, killing any Codex-routed vision turn on the `require_workspace` path.

Root cause: `agent/agent_runtime_helpers.py` assumed `user_message` is always `str`, but for vision turns it arrives as `[{type:"text",...}, {type:"image_url",...}]`.

## Changes
- `agent/agent_runtime_helpers.py`: route `user_message` through the existing `_summarize_user_message_for_log` helper before `.strip()`; widen the param type hint `str` → `Any` to match how it's actually called.
- `tests/agent/test_intent_ack_continuation.py`: regression test that passes a multi-part list on the `require_workspace=True` path; reproduces the exact crash without the fix.
- `scripts/release.py`: AUTHOR_MAP entry for credit.

## Validation
| | Before | After |
|---|---|---|
| Multi-part `user_message` on workspace path | `AttributeError: 'list' object has no attribute 'strip'` | flattened to text, ack detection proceeds |
| `tests/agent/test_intent_ack_continuation.py` | — | 14/14 pass |

## Notes
Salvaged from #9562 by @DataAdvisory. Their diagnosis identified three sites; the two logging/banner previews were fixed independently on `main` by the conversation-loop refactor (both now route through `_summarize_user_message_for_log`). The codex-ack site was still live — this PR fixes it using that same existing helper rather than the redundant new one in the original PR. Authorship preserved.

## Infographic
![PR #9562 infographic](https://v3b.fal.media/files/b/0aa05946/A3VuaXsB9_8g0ZIrvLvxd_23MBKuBm.png)

Nous Research