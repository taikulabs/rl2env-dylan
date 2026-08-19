**fix(agent): merge consecutive same-role contents for native Gemini**

## Summary

Native Gemini multi-tool turns are sendable again — `_build_gemini_contents` now merges adjacent same-role `contents` so parallel tool calls don't produce consecutive `user` turns that Gemini's `generateContent` rejects.

Root cause: the adapter emitted one `contents` entry per source message and never merged adjacent same-role entries. A parallel tool call (N tool results → N `user` `functionResponse` contents), back-to-back user turns, or merged assistant turns each violate Gemini's strict user/model alternation → `HTTP 400 "Please ensure that multiturn requests alternate between user and model"`. Because the offending shape is part of the stored history, every subsequent turn rebuilds the same invalid request and fails again. The sibling converters already merge (`convert_messages_to_anthropic`, `convert_messages_to_converse`); the native Gemini path had no equivalent.

Salvage of #55126 by @MaxFreedomPollard (submitted first). #55329 by @AlexFucuson9 fixed the same issue with an inline approach — both credited; closing as duplicate.

## Changes
- `agent/gemini_native_adapter.py`: after the per-message loop, merge adjacent same-role `contents` by concatenating their `parts`. Single post-pass, handles tool-result grouping, back-to-back user turns, and merged assistant turns uniformly.
- `tests/agent/test_gemini_native_adapter.py`: 2 regression tests (parallel tool results → one user content; consecutive user messages merged).

## Validation
| | Before | After |
|---|---|---|
| `_build_gemini_contents` roles for parallel-tool turn | `[user, model, user, user, user]` → 400 | `[user, model, user]` |
| Parallel `functionResponse`s | split across 2 user contents | grouped in 1 user content |
| `tests/agent/test_gemini_native_adapter.py` | 20 pass | 22 pass |

E2E: ran the exact issue repro through the real adapter — output is `['user', 'model', 'user']` (strict alternation holds), both parallel `functionResponse`s land in the single trailing user content, and the following user text folds into the same turn.

.

## Infographic

![Native Gemini same-role merge](https://v3b.fal.media/files/b/0aa05dc4/PQrlcQAbxPsBh9DarKmyw_xwAH3K7J.png)

Nous Research