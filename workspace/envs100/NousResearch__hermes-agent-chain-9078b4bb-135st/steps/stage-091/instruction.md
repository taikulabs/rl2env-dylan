**feat(cli): track background subagents in the status bar**

## Summary
The CLI status bar now shows a third background-work indicator — `⛓ N` for live background/async subagents — alongside the existing `▶ N` (`/background` agent threads) and `⚙ N` (shell processes from `terminal(background=true)`).

Background subagents (`delegate_task` batches and background single delegations) are long-running work with no at-a-glance visibility until now.

## Changes
- `cli.py` `_get_status_bar_snapshot`: add `active_background_subagents`, sourced from `tools.async_delegation.active_count()` (records still in the `running` state). Wrapped in try/except so a raising `active_count()` leaves the value at 0, matching the `⚙` process-registry guard.
- `cli.py` `_build_status_bar_text` + `_get_status_bar_fragments`: render `⛓ N` after the `⚙` segment in the `<76` and full-width tiers. Omitted on the cramped `<52` tier, same as the other two indicators.
- Tests: 8 new cases mirroring the `▶`/`⚙` suite (snapshot count, exception safety, plain-text + fragment render, and an all-three-coexist case).

## Validation
| | Before | After |
|---|---|---|
| 2 running delegations | no indicator | `⛓ 2` in plain bar + fragments |
| 1 completes | — | drops to `⛓ 1` |
| `active_count()` raises | — | snapshot stays 0, no propagate |

23/23 in `tests/cli/test_cli_background_status_indicator.py` pass. E2E-verified against the real `tools.async_delegation` records dict (not mocked): injecting two `running` records surfaces `⛓ 2`, flipping one to `completed` drops it to `⛓ 1`.

## Infographic

![cli-status-bar-three-background-indicators](https://v3b.fal.media/files/b/0a9f789c/S0QqEDDF_FzT2izhIh51d_dEh4BU4M.png)