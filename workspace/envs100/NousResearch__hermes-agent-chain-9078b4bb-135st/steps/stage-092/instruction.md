**feat(slack): add --no-assistant flag to manifest generation**

## Summary
Adds `--no-assistant` to `hermes slack manifest`, emitting a flat-DM manifest that omits Slack's AI Assistant container (`assistant_view`, `assistant:write`, `assistant_thread_*` events). DMs then render as a normal chat where bare slash commands (`/help`, `/new`) dispatch inline instead of only on `@mention` inside the Assistant thread pane.

Salvage of #51416 by @victor-kyriazakos, cherry-picked onto current main with authorship preserved.

## Why a flag, not a default flip
The Slack adapter actively uses assistant mode: `assistant_threads.setStatus` powers the "is thinking…" indicator, and `assistant_thread_started` seeds session/memory scoping before the first DM message. Defaulting assistant off would silently regress that for every user to fix a slash-in-DM problem that only bites slash-heavy DM users. Assistant-on stays the default; `--no-assistant` is the opt-out. The assistant-on manifest is byte-identical to before (existing test retained).

## Changes
- `hermes_cli/slack_cli.py`: `_build_full_manifest(..., include_assistant=True)`; assistant pieces gated behind the flag
- `hermes_cli/subcommands/slack.py`: `--no-assistant` argparse wiring
- `tests/hermes_cli/test_slack_cli.py`: argparse default/set, omission, core-surface-preserved (7 tests)

## Validation
| | Default | `--no-assistant` |
|---|---|---|
| `assistant_view` | present | dropped |
| `assistant:write` scope | present (14 scopes) | dropped (13 scopes) |
| `assistant_thread_*` events | present | dropped |
| Messages tab / Socket Mode / slashes / channel+DM scopes | kept | kept |

7/7 tests pass. E2E-verified argparse → manifest → JSON for both modes against a temp HERMES_HOME.

.

## Infographic

![slack-no-assistant](https://v3b.fal.media/files/b/0a9f7af9/gIdYhap4legJ6XQKdsHsE_62dCiKdM.png)