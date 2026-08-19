**feat(plugins): namespaced skill registration for plugin skill bundles**

## Summary

Adds `ctx.register_skill()` API so plugins can ship SKILL.md files under a `plugin:skill` namespace, preventing name collisions with built-in Hermes skills. `skill_view()` detects the `:` separator and routes to the plugin registry; bare names continue through the existing flat-tree scan unchanged.

Salvaged from PR #9334 by @N0nb0at (lean P1 — omits the autogen shim for a simpler first merge). Contributor authorship preserved on the main commit.

## Changes

**Source (3 files, ~270 LOC):**
- `agent/skill_utils.py` — `parse_qualified_name()`, `is_valid_namespace()`, `_NAMESPACE_RE`
- `hermes_cli/plugins.py` — `PluginContext.register_skill()`, `PluginManager` skill registry (`find_plugin_skill`, `list_plugin_skills`, `remove_plugin_skill`)
- `tools/skills_tool.py` — Qualified name dispatch in `skill_view()`, `_serve_plugin_skill()` with full guards (disabled, platform, injection scan), bundle context banner with sibling listing, stale registry self-heal. Hoisted `_INJECTION_PATTERNS` to module level (dedup). Updated `SKILL_VIEW_SCHEMA` description.

**Tests (1 file, 27 tests):**
- `tests/test_plugin_skills.py` — Namespace parsing, plugin registry, skill_view qualified dispatch, guards (disabled, platform, injection), banner injection, stale self-heal

**Docs (3 files):**
- `website/docs/guides/build-a-hermes-plugin.md` — Replaced legacy `shutil.copy2` pattern with `ctx.register_skill()` API
- `website/docs/guides/work-with-skills.md` — Added "Plugin-Provided Skills" section
- `website/docs/user-guide/features/plugins.md` — Updated capabilities table

## What's NOT included (deferred from #9334)

- Autogen shim system (`_autogen_plugin_shim`, lock files, 5-case update handler) — this was ~180 LOC of install-time code generation. Can follow up if the `hermes plugins install obra/superpowers` auto-wrapping UX is wanted.
- `build_qualified_name()` — unused outside tests
- `_auto_register_skills_from_dir_v1()` — autogen helper