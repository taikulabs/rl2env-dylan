**feat(tui): track background subagents in the status bar**

## Summary
The Ink TUI status bar now shows `⛓ N` for live background/async subagents — parity with the classic CLI indicator shipped in #51441. Background subagents (`delegate_task` batches and `background=true` single delegations) were invisible in the TUI footer.

## Changes
- `tui_gateway/server.py` `_get_usage()`: embed `active_subagents` from `tools.async_delegation.active_count()` — the same registry the classic CLI reads — onto the existing per-update `usage` payload. Guarded so a raising `active_count()` leaves the field off without breaking the rest of usage.
- `ui-tui` `appChrome.tsx`: new `subagents` status segment (breakpoint `w >= 92`, sheds between `bg` and `cost`), renders `⛓ N` from `usage.active_subagents`.
- `Usage` / `SessionUsageResponse` types gain `active_subagents?`.
- Tests: 3 Python (`_get_usage` count / zero / exception-safe) + 4 Ink (renders, hides on 0/absent, drops on narrow terminal), plus the two existing segment-map tests updated for the new key.

## Validation
| | Before | After |
|---|---|---|
| 2 running delegations | no indicator | `⛓ 2` in status bar |
| 1 completes | — | drops to `⛓ 1` |
| `active_count()` raises | — | field omitted, usage intact |

`test_tui_gateway_server.py` 285/285 pass; Ink `statusRule` + `appChromeStatusRule` 26/26 pass; `npm run build` + `npm run typecheck` clean. E2E-verified against the real `async_delegation` registry through `_get_usage()` (not mocked): 0 → `⛓ 2` → `⛓ 1` as records flip to completed.

Distinct from the turn-scoped `SpawnHud` / `/agents` overlay (those mirror live in-turn `subagent.*` events); this is the persistent registry count, matching the CLI.

## Infographic

![tui-status-bar-background-subagents](https://v3b.fal.media/files/b/0a9f7ae9/gZ1wx2-SAc_kw-9tUVk3K_vTfXC4RS.png)