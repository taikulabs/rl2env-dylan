**fix(agent): count tokens, not just rows, as preflight compression progress (#23767, #39548)**

## Summary

The **preflight** multi-pass compression loop (`agent/turn_context.py`) stopped the moment a pass didn't reduce the message *row count* (`len(messages) >= _orig_len: break`), even when the pass materially reduced *tokens* via tool-result pruning / in-place summarization. On a large session this surfaced a spurious "Cannot compress further" and auto-reset an otherwise healthy session. (Mode "preflight" half of #23767; .)

Companion to #50726, which fixed the same bug class in the 413/context-overflow handlers (`conversation_loop.py`). This PR covers the remaining preflight site.

Salvage of #39574 by @jackjin1997, cherry-picked onto current `main` (authorship preserved) with a maintainer follow-up aligning the progress floor.

## Changes

- `agent/turn_context.py` (contributor): extract `_compression_made_progress()`; re-estimate tokens before the progress check; a pass counts as progress on a row-count drop OR a token-count drop.
- `agent/turn_context.py` (maintainer follow-up): require the token drop to be **material (>5%)** — the same floor the overflow-handler retry path uses — so a sub-5% wobble can't keep the 3-pass loop spinning. Add boundary + zero-token regression tests.
- `tests/agent/test_compression_progress.py`: 9 tests pinning the progress contract.

## Validation

| | Result |
|---|---|
| `tests/agent/test_compression_progress.py` (+2) | 9 passed |
| `tests/run_agent/test_413_compression.py` (preflight subset) | 11 passed |
| `tests/agent/test_turn_context.py` | 10 passed |
| ruff (diff vs main) | clean |

Part of #23767 (does not close it — modes A/B/F still pending).

. (Bug #39548 already closed.)

Co-authored-by: JackJin <1037461232@qq.com>

## Infographic

_Image generation is unavailable in this environment (FAL_KEY unset, no managed-provider credits); to be attached once available._