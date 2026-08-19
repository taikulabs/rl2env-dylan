**fix(discord): warn on 32-char clamp collisions in the /skill collector**

## Summary

Closes out the "Discord `/skill` commands not finding a skill" series (follows #18745, #18753, #18754).

Discord's per-command name limit is 32 chars. When two skill slugs share the same first 32 chars — or a skill slug clamps onto a reserved gateway command name — only the first seen wins; the second is dropped from the `/skill` autocomplete. The old behavior incremented `hidden` **silently**, so skill authors had no way to discover the drop short of noticing their skill was missing from the picker.

Not actively biting today (no collisions on the default catalog as of 2026-05), but a landmine the moment someone ships a long-named skill. The earlier PRs in this series closed the other silent data-loss paths in the Discord `/skill` collector; this is the last remaining one.

## Fix

Promote `_names_used` from a `set` to a `dict` keyed by the clamped name, mapping to the originating cmd_key (or a `"<reserved>"` sentinel for `reserved_names`). On collision, log a WARNING naming both sides — winner, loser, clamped name, and the remediation.

Two phrasings:

- **skill-vs-skill** — *"both clamp to X on Discord's 32-char command-name limit; only the winner appears in `/skill`. Rename one skill's frontmatter `name:` to differ in its first 32 chars."*
- **skill-vs-reserved** — *"collides with a reserved gateway command name; the skill will not appear in `/skill`. Rename the skill's frontmatter `name:`."*

## Tests

`tests/hermes_cli/test_discord_skill_clamp_warning.py` — three cases:

1. `test_clamp_collision_emits_warning_naming_both_skills` — two 40-char slugs sharing a 32-char prefix; warning names both cmd_keys + the clamped prefix, `hidden == 1`, alphabetical winner is kept.
2. `test_clamp_collision_with_reserved_name_emits_distinct_warning` — skill slug clashes with a reserved gateway command; warning uses the distinct "reserved" phrasing.
3. `test_no_collision_no_warning` — two distinct-prefix skills; zero warnings emitted, both registered.

All three pass; 133 surrounding `test_commands.py` tests still pass.

## Series

- #18745 — drop legacy 25×25 caps + complete #18741's external_dirs fix in the Discord collector.
- #18753 — match disabled/optional skills by frontmatter slug, not directory name.
- #18754 — `/reload-skills` refreshes the live Discord `/skill` autocomplete.
- **this PR** — warn (don't silently drop) on 32-char clamp collisions.