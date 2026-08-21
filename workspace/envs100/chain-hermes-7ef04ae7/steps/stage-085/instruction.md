**fix(agent): merge consecutive assistant messages before API replay (#29148, #49147)**

## Summary

Strict OpenAI-compatible providers now accept replayed histories that contain consecutive assistant messages — `repair_message_sequence()` collapses them into a single assistant turn before every API call.

Root cause: DeepSeek v4, Moonshot/Kimi and similar strict providers reject a history where an `assistant` message carrying `tool_calls` is immediately followed by another `assistant` message instead of its `tool` results (`HTTP 400 — "An assistant message with 'tool_calls' must be followed by tool messages…"`). `repair_message_sequence` — the defensive belt run before every API call — fixed orphan-tool and consecutive-user shapes but **never merged consecutive assistant messages**. That gap is the bug.

The split shape is produced by recovery/continuation paths that append an interim assistant turn (thinking-prefill, codex incomplete-continuation) and by host-fed / legacy-persisted / resumed histories. The serializer itself is 1:1 and never splits — verified by repro — so the fix belongs in the repair pass, not serialization.

This consolidates three contributor PRs (#29168 @Bartok9, #49162 @woaini30050, #34510 @weidzhou) that each fixed one half of the problem, into a single pass covering both reported shapes.

## Changes
- `agent/agent_runtime_helpers.py`: add **Pass 0** to `repair_message_sequence()` — merges adjacent `assistant` messages (union of `tool_calls`, concatenated `content`, carried `reasoning_content`). Runs before Pass 1 so the merged union of tool_call ids is known to the orphan-tool filter. A `tool` result or `user` turn between two assistants blocks the merge (distinct, valid rounds).
- `tests/run_agent/test_message_sequence_repair.py`: 8 regression tests.

## Shapes handled
| Input | Result |
|---|---|
| `assistant(tc=[A])` → `assistant(tc=[B])` (parallel split, #29148) | `assistant(tc=[A,B])` |
| `assistant(content)` → `assistant(tc=[A])` (content-then-tool, #49147) | `assistant(content, tc=[A])` |
| 3× consecutive `assistant(tc)` | one turn, 3 tool_calls |
| two text-only assistants | one merged text turn |
| `assistant(tc)` → **`tool`** → `assistant(tc)` | **not merged** (distinct rounds) |
| `assistant` → **`user`** → `assistant` | **not merged** (normal dialog) |
| already-valid single `assistant(tc=[A,B])` | unchanged (repairs == 0) |

## Validation
| | Before | After |
|---|---|---|
| `repair_message_sequence` on split shape | left consecutive assistants → DeepSeek 400 | merged into one valid turn |
| `tests/run_agent/test_message_sequence_repair.py` | 16 pass | 24 pass |
| Live DeepSeek replay of repaired #49147 shape | n/a | HTTP 200, summarized correctly |
| orphan-tool / consecutive-user passes | pass | pass (unchanged) |

E2E: ran the real `repair_message_sequence` on the exact #29148 and #49147 shapes, asserted the output is structurally valid (every `assistant(tool_calls)` immediately followed by its `tool` results, no consecutive assistants), then replayed the repaired #49147 history to `deepseek/deepseek-chat-v3.1` — 200 OK.

, .

## Infographic

![Consecutive assistant merge](https://v3b.fal.media/files/b/0aa05cca/yLCOGqt9GIxemnmLbpCCt_x4YdxRyF.png)

Nous Research

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/run_agent/test_message_sequence_repair.py`