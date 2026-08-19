**fix(approval): catch hermes gateway stop/restart behind a profile flag**

## Summary
`hermes -p <profile> gateway restart` is now flagged by the approval layer — a profile flag between `hermes` and `gateway` no longer slips the agent past the gateway-lifecycle guard. That gap is the exact form from the 2026-04-11 ade-profile self-kill loop.

Root cause: the guard's hermes-CLI pattern required `hermes` and `gateway` to be adjacent (`\bhermes\s+gateway\s+(stop|restart)\b`), so any global flag in between defeated it.

## Changes
- `tools/approval.py`: allow an optional run of global flags (`-p ade`, `--profile ade`, multiple flags) between `hermes` and the `gateway stop|restart` subcommand.
- `tests/tools/test_approval.py`: +7 tests covering the profile-flag forms and the still-safe `start`/`status` negatives.

## Validation
| Command | Before | After |
|---|---|---|
| `hermes gateway stop` | flagged | flagged |
| `hermes -p ade gateway restart` | **not flagged** | flagged |
| `hermes --profile ade gateway stop` | **not flagged** | flagged |
| `hermes -p cocoa --verbose gateway restart` | **not flagged** | flagged |
| `hermes -p ade gateway status` | not flagged | not flagged |
| `hermes gateway start` | not flagged | not flagged |

`scripts/run_tests.sh tests/tools/test_approval.py` → 252 passed, 0 failed.

## Relationship to #7817
Supersedes #7817 (@BrownBear127). That PR proposed adding a separate launchctl block + a `hermes … gateway (restart|stop|kill)` pattern. The launchctl half is already fully covered on `main` by #33071 (`launchctl (stop|kickstart|bootout|unload|kill|disable|remove) … hermes`), and `gateway kill` is not a real subcommand. This change narrows the one genuine residual gap — the profile-flag adjacency — without redundant patterns.

## Infographic
![infographic](https://v3b.fal.media/files/b/0aa05944/KLI8jBOw9MUFW7cfch-0t_BGypaRQC.png)