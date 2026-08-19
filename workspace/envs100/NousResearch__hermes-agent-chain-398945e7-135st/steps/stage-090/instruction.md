**fix(discord): complete #18741 for /skill autocomplete and drop legacy 25x25 caps**

## Summary

`discord_skill_commands_by_category` — the collector the live `/skill` Discord autocomplete calls — was lagging its sibling `discord_skill_commands` on two counts, both silently dropping skills users expected to see.

### 1. External-dir skills were filtered out

#18741 widened the flat `discord_skill_commands` collector to accept `SKILLS_DIR + skills.external_dirs`. It left the `by_category` variant still matching `SKILLS_DIR` only. That variant is the one `_register_skill_group` (`gateway/platforms/discord.py`) calls for Discord's `/skill` command, so external-dir skills stayed invisible in the Discord autocomplete despite showing up everywhere else (`hermes skills list`, the agent's `/skill-name` dispatch).

Fix: widen the accepted roots to match, and derive categories from whichever root the skill lives under so `<ext>/mlops/foo/SKILL.md` still lands in the `mlops` group.

### 2. Legacy 25×25 caps from the old nested layout were still being applied

PR #11580 refactored `/skill` to a flat autocomplete layout (Discord fetches options dynamically — no per-command payload concern). Its docstring promises "no hidden skills." But the `by_category` collector kept the old `_MAX_GROUPS=25` × `_MAX_PER_GROUP=25` caps from the nested `/skill <cat> <name>` layout, silently dropping anything past the 25th alphabetical category.

Real user impact: installs with 29+ category dirs (the tail — `social-media`, `software-development`, `yuanbao`, etc.) were losing entire categories from autocomplete, logged only as `"N skill(s) filtered out of /skill (name clamp / reserved)"`.

Fix: remove the caps. `hidden` is retained in the return shape for backward compatibility and now reports only genuine 32-char name-clamp collisions against reserved names.