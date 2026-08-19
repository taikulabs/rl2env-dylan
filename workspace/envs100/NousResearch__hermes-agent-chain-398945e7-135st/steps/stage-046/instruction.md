**fix: surface self-improvement review summaries across CLI, TUI, and gateway**

## Summary
The self-improvement background review's `💾 …` summary (the line that tells you it patched a skill or saved a memory entry) now reliably surfaces to the user across every interface — CLI, Ink TUI (`hermes --tui` + dashboard `/chat`), and messaging gateways — and is attributed to the self-improvement loop so it's unambiguous.

## Root cause
Real-world trigger: on 2026-04-30 the `hermes-release` skill was patched at 11:33:47 by a bg review (`.usage.json` records it) but no `💾` ever appeared in the still-open CLI session. Three silent failure modes:

1. **CLI:** bg-thread `_cprint` called `prompt_toolkit.print_formatted_text` directly while a `PromptSession` was live → raced with the input-area redraw, line could end up buried.
2. **TUI:** no wiring at all — the bg review had no surface to speak to. `agent.background_review_callback` was never set by the tui_gateway, so Ink never saw the summary.
3. **Attribution:** even when the line did land, `💾 Skill updated` gave no hint the self-improvement loop was responsible.

## Changes
- `cli._cprint`: detect cross-thread invocation with a live PT `Application`; schedule `run_in_terminal` via `loop.call_soon_threadsafe`. Input pauses, line prints clean, prompt redraws. Direct-print fallbacks preserved for no-app, same-thread, import-error, and attribute-error paths. Fixes every bg-thread emission (curator summaries, aux failures), not just the review.
- `run_agent._spawn_background_review`: summary now reads `  💾 Self-improvement review: <actions>` in both the `_safe_print` path (CLI) and the `background_review_callback` path (TUI + gateway).
- `tui_gateway/server.py`: in `_init_session`, attach `agent.background_review_callback` to an `_emit('review.summary', sid, {text})` closure. Safe on agents with locked `__slots__`.
- `ui-tui/src/app/createGatewayEventHandler.ts`: new `review.summary` case routes `payload.text` through `sys(…)` so it persists in the transcript, matching the `background.complete` pattern. Empty / whitespace payloads are ignored.
- `ui-tui/src/gatewayTypes.ts`: extend `GatewayEvent` union with `{ type: 'review.summary', payload?: { text?: string } }`.
- **Gateway platforms** (Telegram, Discord, Slack, …): no code changes — existing `background_review_callback` post-delivery queue in `gateway/run.py` picks up the new prefix string automatically.

## Validation
| | Before | After |
|---|---|---|
| CLI bg-thread `_cprint` w/ live app | direct `_pt_print` races w/ prompt redraw | schedules `run_in_terminal` via app loop |
| TUI review summary delivery | silent, no callback wired | `review.summary` event → `sys(…)` transcript line |
| Gateway review summary delivery | `💾 Skill created.` | `💾 Self-improvement review: Skill created.` |
| Attribution | none | `💾 Self-improvement review: <actions>` everywhere |
| Python tests | — | 19 passed (6 new `_cprint` routing, 1 new bg-review prefix, 2 new tui_gateway callback) |
| tui_gateway suite | — | 64/64 pass |
| cli + run_agent suites | — | 588 + 1176 pass, 17 skipped |
| Ink vitest | — | 36/36 pass (3 new for `review.summary`) |
| TypeScript type-check | — | clean |
| Live E2E (Python) | — | bg thread `_cprint` correctly schedules `run_in_terminal` inside a real PT Application |

## Scope limits
Unchanged: nudge thresholds, review prompt text, summary-action detection, gateway platform adapters, memory/skill core code. Surgical across three surfaces.