**feat(discord): register skills under /skill command group with category subcommands**

## Summary

Instead of consuming one top-level slash command slot per skill (hitting the 100-command limit with ~26 built-ins + 74 skills), skills are now organized under a single `/skill` group command with category-based subcommand groups:

```
/skill creative ascii-art [args]
/skill media gif-search [args]  
/skill mlops axolotl [args]
/skill dogfood [args]  ← uncategorized (root-level)
```

**Discord supports 25 subcommand groups × 25 subcommands = 625 max skills** — well beyond the previous 74-slot ceiling. Uses only 1 top-level command slot instead of N.

## How it works

Categories are derived from the skill directory structure:
- `skills/creative/ascii-art/` → category `creative`
- `skills/mlops/training/axolotl/` → category `mlops` (uses top-level parent)
- `skills/dogfood/` → uncategorized (direct subcommand of `/skill`)

## Changes

| File | What |
|------|------|
| `hermes_cli/commands.py` | New `discord_skill_commands_by_category()` — groups skills by category, filters hub/disabled, enforces Discord limits |
| `gateway/platforms/discord.py` | New `_register_skill_group()` — builds `app_commands.Group` hierarchy; replaces old top-level skill registration |
| `tests/gateway/test_discord_slash_commands.py` | 3 new tests + updated mocks for Group/Command |
| `tests/hermes_cli/test_commands.py` | 4 new tests for category grouping logic |

## Test results

- 20/20 Discord slash command tests pass
- 108/108 commands tests pass
- 535/535 gateway tests pass (2 pre-existing flaky errors in reply_mode unrelated to this PR)

Inspired by Discord community suggestion from bottium.