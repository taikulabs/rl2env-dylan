**fix(cli): clear input-blocking overlays when interrupting a running agent**

## Summary

Interrupting the agent while an approval / clarify / sudo / secret prompt is open no longer freezes the CLI. Salvage of #14026 by @neo-2026, reapplied onto current `main` and widened.

**Root cause:** each of those prompts blocks a worker thread on a `response_queue.get()`. On interrupt the worker thread is torn down, but the overlay's state dict stays set — so `read_only` (gated on `_command_running`) plus the keypress filter keep CLI input locked, with nothing servicing the prompt. The terminal appears dead until the prompt's own timeout expires.

## Changes

- `cli.py`: new `_clear_active_overlays_for_interrupt()` chokepoint drains and nils all four input-blocking overlays — approval → `deny`, clarify/sudo/secret → cancel — each step guarded so a dead queue can't block clearing the others; sudo restores the pre-modal draft.
- Wired into all three interrupt paths: the new-message interrupt loop, `handle_ctrl_c`, and `handle_ctrl_q` (the sibling handler the original PR missed — same bug class).
- Blocking overlays now clear **and** fall through, so one keypress both clears a stale overlay and interrupts a still-running agent. The `/model` picker and slash-confirm foreground prompts keep their cancel-and-return behavior.
- `tests/cli/test_cli_approval_ui.py`: 4 regression tests exercising the real helper (all-four cleanup, no-op when idle, dead-queue resilience, end-to-end thread unblock).
- `scripts/release.py`: AUTHOR_MAP entry for the contributor.

## Validation

| | Before | After |
|---|---|---|
| Interrupt with overlay open | input frozen until prompt timeout | overlay cleared, input freed instantly |
| Blocked worker thread | stays blocked | unblocks (receives `deny`) |
| Targeted suite | — | 26/26 pass |

Live before/after test (real threads): with the fix the blocked worker unblocks and `_command_running` frees; the control path (no cleanup) reproduces the freeze to timeout.

. Salvages #14026.

## Infographic

![Clear overlays on interrupt](https://v3b.fal.media/files/b/0aa05bdd/4IM-VgXzcHqmCtNhaPKU1_8DgHkvnn.png)