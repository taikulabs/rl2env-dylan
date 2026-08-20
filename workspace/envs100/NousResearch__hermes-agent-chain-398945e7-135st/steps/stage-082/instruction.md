**fix(gateway): match disabled/optional skills by frontmatter slug, not dir name**

## Summary

`_check_unavailable_skill` (gateway/run.py) turns a failed "/foo" lookup into a pointed hint — *"disabled, enable with `hermes skills config`"* or *"available but not installed, install with `hermes skills install …`"* — instead of the bare *"unknown command"*. It was doing the match by comparing `skill_md.parent.name` (the directory name, lowercased with underscores swapped to hyphens) against the typed command, which silently misses every skill whose directory name drifted from the declared frontmatter `name:`.

On a current install **19 skills** hit that drift. Examples:

| dir | registered slug (what users type) |
|-----|-----------------------------------|
| `mlops/stable-diffusion` | `/stable-diffusion-image-generation` |
| `mlops/qdrant` | `/qdrant-vector-search` |
| `mlops/saelens` | `/sparse-autoencoder-training` |
| `mlops/flash-attention` | `/optimizing-attention-flash` |
| `mlops/modal` | `/modal-serverless-gpu` |

In every one of those cases, `_check_unavailable_skill` would compare `stable-diffusion` to `stable-diffusion-image-generation` and return `None`, so the user got the generic unknown-command reply even though the disabled/optional hint was exactly what the function is there to produce.

## Fix

Extract a small `_skill_slug_from_frontmatter(skill_md)` helper that reads the SKILL.md frontmatter and normalizes exactly like `agent.skill_commands.scan_skill_commands` (lowercase, spaces/underscores → hyphens, strip anything outside `[a-z0-9-]`, collapse runs of hyphens, strip edges). Use it in both branches of `_check_unavailable_skill`:

- disabled-skills branch: `slug == normalized and declared_name in disabled` — the disabled set is keyed by the declared frontmatter name (that's what `hermes skills config` / `save_disabled_skills` writes), which is independent from the slug.
- optional-skills branch: match on `slug` alone.

## Tests

Five new tests in `tests/gateway/test_unavailable_skill_hint.py`, all failing on main and passing with the fix:

1. Drift case, disabled branch — `dir=stable-diffusion` + `name: Stable Diffusion Image Generation` → typing `stable-diffusion-image-generation` yields the disabled hint.
2. Unknown command still returns `None`.
3. Matched-but-not-disabled still returns `None`.
4. Non-alnum chars are stripped (`C++ Code Review` → `c-code-review`).
5. Drift case, optional-skills branch — same directory/name shape yields the "not installed" hint with the correct `official/mlops/stable-diffusion` install path.

## Related

- Part of a series triaging "Discord /skill commands not finding a skill" (#18745 shipped the first: 25×25 cap + external_dirs completion of #18741).
- This one covers the *typed* slash command path on every platform, not just Discord.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_unavailable_skill_hint.py`