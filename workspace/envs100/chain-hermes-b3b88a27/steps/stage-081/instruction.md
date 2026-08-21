**fix: eliminate <think> leakage across storage, API replay, and /resume**

## Summary
Inline reasoning tags (`<think>…</think>` and friends) no longer leak to users on messaging platforms, into session titles, into the `/resume` recap, or into the assistant content replayed to the API on subsequent turns.

Root cause: `_build_assistant_message()` stored the raw `content` verbatim, and `_strip_think_blocks()` left unterminated `<think>…EOF` (dropped close tag on NIM/MiniMax M2.7) untouched.

Consolidates 4 open PRs (#9250, #9306, #10408, #11366) and retires 3 stale/superseded PRs (#9007, #9052, #9587).

## Changes
- `run_agent.py::_strip_think_blocks` — case-insensitive closed-pair regexes for every variant, new block-boundary pass that strips unterminated tags from open → EOF, existing orphan-close sweep retained.
- `run_agent.py::_build_assistant_message` — one strip at the storage boundary so API replay, session transcript, gateway delivery, CLI display, compression, and title generation all see clean content.
- `cli.py::_strip_reasoning_tags` — adds `<thought>` (Gemma 4), adds orphan-close sweep, `IGNORECASE` applied to all passes, drops redundant duplicate casing entries.
- Regression tests: 6 in `TestStripThinkBlocks`, 3 in `TestBuildAssistantMessage`, 7 in `test_resume_display.py`.

## Validation
| | Before | After |
|---|---|---|
| `TestStripThinkBlocks` | 10 passing | 16 passing |
| `TestBuildAssistantMessage` | 7 passing | 10 passing |
| `test_resume_display.py` | 29 passing | 36 passing |
| MiniMax unterminated `<think>never closes` | leaks content | stripped to `""` |
| `<think>hidden</think>Visible` via `/resume` | leaks `hidden` | shows `Visible` |

E2E verified with real imports against the worktree (isolated `HERMES_HOME`): closed-pair, unterminated, mid-response, mixed-case, multi-block, prose-mention non-regression all behave as intended.

## Closes
- #8878 — Think/reasoning tags visible to users on messaging platforms
- #9568 — Every conversation includes a think tag
- #11316 — `/resume` recap can leak hidden reasoning blocks wrapped in `<think>` tags

(#9685 was already resolved by ` — the streaming path filter. The recap, storage, and unterminated paths remained and are covered here.)

## Credit
- @Tranquil-Flow — PR #9250 approach (strip at `_build_assistant_message`); authorship preserved on `.
- @yeyitech — PR #11366 approach (`_strip_reasoning_tags` expansion + recap tests); authorship preserved on `.
- @luinbytes — PR #10408 identified the NIM/MiniMax unterminated-tag symptom. This PR does not include the `💭`/`🧠` emoji regexes from that PR — those glyphs are hermes CLI display decorations, not model content markers, and stripping them would false-positive on any response that mentions those emojis.
- @luoyejiaoe-source — PR #9306 quantified the context-bloat impact (55% of assistant messages on MiniMax started with `<think>`, 16% content-size reduction). Their approach (strip at API-send time) is superseded by storage-time stripping, which cleans every downstream consumer in one place.

## Superseded / closing after merge
- #9007 (configurable show_reasoning for raw tags) — stale against current stream consumer architecture; raw tags always suppressed, clean extracted reasoning is shown when `show_reasoning` is on.
- #9052 (whitespace strip + duplicate `_build_assistant_message` fix + unrelated BlueBubbles changes) — think-block portion duplicates #9250.
- #9306 — superseded by storage-time strip (#9250 approach).
- #9587 — redundant after storage-time strip.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/cli/test_resume_display.py`