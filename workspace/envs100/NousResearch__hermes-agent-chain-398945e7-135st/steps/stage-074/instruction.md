**fix(deepseek): use non-empty reasoning_content placeholder for V4 Pro thinking mode**

DeepSeek V4 Pro rejects empty-string `reasoning_content` in thinking mode with HTTP 400. Salvages #17341 and widens the fix to every injection site + stale sessions.

## Changes
- `run_agent.py`: replace `""` with `" "` at all three injection sites
  - `_build_assistant_message` tool-call pad (#15250 / #17400 path)
  - `_copy_reasoning_content_for_api` cross-provider poison guard (#15748 path)
  - `_copy_reasoning_content_for_api` unconditional thinking pad
- `run_agent.py`: upgrade stale `reasoning_content=""` → `" "` on replay when the active provider enforces thinking-mode echo (so sessions persisted before this change don't 400 on their first V4 Pro turn after updating)
- 9 existing assertions flipped to `" "`; 2 new regression tests (stale upgrade on DeepSeek V4 Pro, verbatim preservation on non-thinking providers)
- `scripts/release.py`: AUTHOR_MAP entry for IMHaoyan

## Validation
| | Before | After |
|---|---|---|
| DeepSeek V4 Pro thinking-mode multi-turn tool calls | 400 `reasoning content in the thinking mode must be passed back` | OK |
| Older DeepSeek (`""` tolerated) | OK | OK (space also accepted) |
| Non-thinking providers with empty `reasoning_content` | verbatim `""` | verbatim `""` |
| Test suite (reasoning/deepseek/kimi/thinking) | — | 160 passed, 3 skipped |
| `tests/run_agent/` full | — | 1190 passed (2 failing concurrent_interrupt tests are unrelated, also fail on origin/main) |

 — credit to @IMHaoyan whose commit authorship is preserved on the only commit in this branch.