**fix(gateway): stop per-turn agent-cache eviction from model + message_id signature churn**

## Summary

Stops the gateway from evicting the cached `AIAgent` on every turn, so the prompt cache can actually warm. Two independent signature-churn bugs caused a rebuild every message.

## Changes

- `gateway/run.py` (fallback-eviction): normalize `_cfg_model` the same way `AIAgent.__init__` does before comparing to `_agent.model`, so a vendor-prefixed config value (`deepseek/deepseek-v4-pro`) matches the stripped agent model (`deepseek-v4-pro`) on native providers. Aggregators (openrouter, etc.) keep the vendor/model slug and are left untouched. *(contributor's fix)*
- `gateway/session.py` + `gateway/run.py`: the Discord triggering `message_id` no longer goes into the cached system prompt (it changes every turn → busts the agent-cache signature). The volatile id is injected per-turn into the user message; the cached IDs block carries a static pointer so reply/react/pin via the discord tools still works.
- `tests/gateway/test_session.py`: regression test asserting the cached prompt is byte-stable across changing `message_id`.
- `scripts/release.py`: AUTHOR_MAP entry for @fayenix.

## Root cause

| Bug | Before | After |
|---|---|---|
| Model mismatch | `agent.model != _cfg_model` always true for vendor-prefixed native config → evict every successful turn | normalized, matches → no false eviction |
| `message_id` in cached prompt | sig changes every Discord turn → rebuild every message | id moved to per-turn user message; cached prompt stable |

## Validation

- E2E: `build_session_context_prompt()` is now identical across message_ids 1001/2002/3003; raw id absent from the cached prompt; static pointer present. `normalize_model_for_provider('deepseek/deepseek-chat','deepseek')` → `deepseek-chat` (matches); openrouter slug untouched.
- `scripts/run_tests.sh tests/gateway/test_session.py tests/gateway/test_agent_cache.py` → 165 passed.

## Salvage notes

Adapted from #28846 (@fayenix). Bug 1's fix is the contributor's. Bug 2 was reworked to be **non-destructive** — the original PR deleted the triggering-message line outright (killing reply/react/pin); this keeps the capability and just moves the volatile id off the cached prefix. The original PR's auto-reset eviction block is already on main (#9893/#48031) and the `reset_context_note` "scoping bug" did not reproduce on current main, so both were dropped.

## Infographic

![infographic](https://v3b.fal.media/files/b/0aa05c8d/QbqovVjd7yJACu_gF_kt0_VlAE4rou.png)