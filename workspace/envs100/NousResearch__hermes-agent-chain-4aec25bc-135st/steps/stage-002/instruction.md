**fix(deepseek): wire thinking-mode via DeepSeekProfile (, #17212, #17825)**

## Summary
DeepSeek V4 / `deepseek-reasoner` requests now go out with the explicit `extra_body.thinking` + `reasoning_effort` parameters they require, instead of silently defaulting to thinking-on and 400ing on the next turn.

**Root cause.** DeepSeek has a registered `ProviderProfile`, so requests go through `_build_kwargs_from_profile`. The base profile's `build_api_kwargs_extras` returns `({}, {})` — so every request to `api.deepseek.com` went out with no `thinking` parameter and no `reasoning_effort`. DeepSeek defaults to `thinking=enabled`, returns `reasoning_content`, then 400s on subsequent turns. Confirmed empirically by instantiating the live profile.

@tw2818's PR #15251 correctly diagnosed this but placed the fix in `build_kwargs`'s legacy fallback path, which DeepSeek never reaches. Cherry-picked their commit to preserve authorship, then pivoted the fix to the profile path in the follow-up commit.

## Changes
- `plugins/model-providers/deepseek/__init__.py`: new `DeepSeekProfile(ProviderProfile)` mirroring `KimiProfile`. Emits `extra_body.thinking = {type: enabled|disabled}` + top-level `reasoning_effort`. Model gating: V4 family + `deepseek-reasoner` only; `deepseek-chat` (V3) untouched.
- `scripts/release.py`: AUTHOR_MAP entry for @tw2818.
- `tests/plugins/model_providers/test_deepseek_profile.py`: 26 unit tests pinning wire shape, model gating, effort mapping, and full-kwargs integration through the transport.

## Validation
| | Before | After |
|---|---|---|
| `deepseek-v4-pro` wire format | `{}` (no thinking, no effort) | `{reasoning_effort, extra_body.thinking}` |
| Wire format matches live test | no | yes (matches `tests/run_agent/test_deepseek_v4_thinking_live.py::_thinking_kwargs`) |
| New tests | n/a | 26/26 passing |
| Transport + provider profile suites | 321 passing | 321 passing (no regressions) |

.
.
.

Co-authored-by: tw2818 <twebefy@gmail.com>