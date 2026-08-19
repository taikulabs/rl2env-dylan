**fix(memory): zero-match feedback + graceful degrade to stop at-capacity retry-loop hang**

## Summary

Fixes the silent hang where memory at capacity sends the agent into a `replace`/`add` retry loop that exhausts the turn and delivers **no reply**. Two layers: (1) the zero-match branch now returns entry previews so the model can self-correct, and (2) a per-turn consolidation-failure cap makes a failed memory side-effect degrade gracefully instead of looping the turn to death.

Salvaged from #42522 by @kyssta-exe (zero-match feedback) with the regression-test coverage from #42417 by @liuhao1024; the graceful-degrade layer + batch coverage are a follow-up commit. Supersedes #42417, #16277, #16373 (all narrower takes on the same zero-match feedback).

## Changes

**Commit 1 (@kyssta-exe, #42522) — zero-match feedback (issue ):**
- `tools/memory_tool.py`: `replace`/`remove` zero-match and the `add`-overflow error now return `previews` + `current_entries` with actionable "retry with the exact text" guidance, matching the multi-match branch. The model can see what's stored and self-correct instead of retrying blind.

**Commit 2 (follow-up) — graceful degrade (issue ):**
- `MemoryStore` tracks per-turn consolidation failures; after a cap (3) it drops the "retry — all in this turn" instruction and returns a terminal "leave memory unchanged, continue your reply" result, so a failed memory side-effect can never block the turn's reply. Counter resets on any successful write and at each turn boundary (`turn_context`, `getattr`-guarded so plugin stores without the method are a no-op).
- **Whole bug class:** `apply_batch` (the primary at-capacity consolidation path the prompts steer toward) and `_batch_error` now route through the same counter — a looping failing batch degrades identically to the single-op loop.

This stays surgical: it does **not** flip the global `tool_loop_guardrails.hard_stop_enabled` default (deliberately opt-in for interactive sessions); the memory tool degrades on its own regardless of that setting.

## Validation

| Scenario | Before | After |
|---|---|---|
| `replace`/`remove` zero-match | bare "No entry matched" — agent loops blind | returns previews + current_entries → agent self-corrects |
| Memory at cap, model can't land an exact consolidation | loops add↔replace/batch to budget exhaustion → no reply (silent hang) | after 3 failed attempts, terminal "stop, continue your reply" → reply always delivered |
| Looping failing `apply_batch` | same hang on the batch path | degrades identically (shared per-turn budget) |
| Legitimate multi-step consolidation | — | unaffected; counter resets on each success |

- 97 targeted tests pass (`tests/tools/test_memory_tool.py`, `tests/agent/test_turn_context.py`), incl. 7 new graceful-degrade tests covering the cap boundary, cross-action shared budget, batch path, success-reset, and turn-boundary reset.
- Mutation-checked: the degrade tests fail under a "never degrade" / "batch not counted" mutation.
- Prompt-cache safe: no system-prompt or past-context mutation; previews appear only in tool-result payloads.