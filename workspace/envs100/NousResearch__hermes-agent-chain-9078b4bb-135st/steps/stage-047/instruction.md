**feat(cli): /reasoning full — show complete thinking, not 10-line clamp**

## Summary
`/reasoning full` now prints the complete model thinking in the post-response recap box instead of clamping it to the first 10 lines.

Live streaming already showed reasoning in full, but the recap box rendered after a turn hard-truncated long traces to 10 lines with no escape hatch — the reason some users reach for other tools when seeing the whole thinking matters. This adds an opt-in toggle.

## Changes
- `hermes_cli/config.py` + `cli.py`: new `display.reasoning_full` (default `false`) + instance attr.
- `cli.py`: the recap clamp now only collapses when `reasoning_full` is off; the truncation note points at the command.
- `hermes_cli/cli_commands_mixin.py`: `/reasoning full|clamp` (aliases `all`/`collapse`) toggles + persists the flag; status line shows full vs clamped.
- `hermes_cli/commands.py`: updated args hint + completions.

## Validation
| | Before | After |
|---|---|---|
| `/reasoning` (long trace) | recap clamped to 10 lines, no override | `/reasoning full` shows all; `/reasoning clamp` restores 10 |
| Default behaviour | clamped | clamped (unchanged) |

`tests/hermes_cli/test_reasoning_full_command.py` — 5 passing (toggle sets flag, persists to config.yaml both ways, `all` alias, clamp-gate invariant).

## TUI parity
`/reasoning full|clamp` now works in the TUI too (`tui_gateway` `config.set reasoning`). The TUI never had the 10-line recap clamp — it renders thinking as an expand/collapse section — so `full` maps to `sections.thinking=expanded` (raw, uncapped) and `clamp` to `collapsed`; `display.reasoning_full` is persisted for cross-surface consistency. Previously `/reasoning full` errored in the TUI (`unknown reasoning value`). Test added in `tests/test_tui_gateway_server.py`.

## Infographic

![reasoning-full](https://v3b.fal.media/files/b/0a9f4129/3YYi7tk9U6Dxc6A3-GG45_CHNogND5.png)