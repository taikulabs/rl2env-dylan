**fix(config): route every migration write through one default-stripping chokepoint**

## Summary
`hermes update` / `hermes -p` no longer rewrites a hand-curated `config.yaml` into a near-full `DEFAULT_CONFIG` dump on a version bump. All config migration writes now flow through a single default-stripping chokepoint, so only values that differ from the schema default (plus explicit user-data removals/renames) ever land on disk — defaults merge transparently at read time via `load_config()`.

**Root cause:** `migrate_config()` had ~16 independent `save_config()` call sites. Each migration author decided ad hoc whether to materialise a value, and many persisted pure schema defaults with `strip_defaults=False`, bypassing the default-stripping protection added in #27539/#53132. Because there was no single rule, every prior fix patched individual sites and the bug-class kept returning. Writing a default to disk is not just bloat — it shadows future default changes (the on-disk value wins the merge forever).

## Changes
- `hermes_cli/config.py`:
  - New `_persist_migration(config)` chokepoint — a thin wrapper over `save_config(config)` (default-stripping ON) documenting the migration write invariant.
  - All 17 migration write sites (including the version-bump finalizer) route through it; `strip_defaults=False` is gone from the migration path.
  - The catch-all `get_missing_config_fields()` finalizer no longer injects every missing default to disk — it only surfaces the list for the informational "N new config option(s) available" display and persists the version bump.
- `tests/hermes_cli/test_config.py`:
  - `TestMigrationWriteInvariant` — AST guard asserting `migrate_config()` makes **no** direct `save_config()` call (regression-proof), plus a full-range v1→latest leanness test.
  - Two change-detector tests that froze the on-disk representation of default-valued keys (`write_approval`, `interim_assistant_messages`) rewritten to assert the **effective** value via `load_config()` (behavior contract, not snapshot).

## The invariant (enforced in one place)
A migration may persist only values that **differ from the current schema default**, plus explicit removals/renames of user data. Verified empirically for every category:
- pure-default seeds (timezone, curator/auxiliary.curator blocks, interim flag, curator.consolidate, empty plugins.enabled) → stripped, merged in at read time;
- non-default values (write_approval=True, ttl_hours=1) → preserved via `save_config`'s explicit-raw-path preservation;
- behavior flips (agent.verify_on_stop=False, whose schema default is still `"auto"`) → preserved because `False != "auto"`;
- data transforms (custom_providers→providers, stt.model relocation, write_mode→write_approval, compression.summary_* removal, MCP-disable) → persist their removals/renames.

An explicitly user-set non-default value (e.g. `matrix.require_mention: false`) is preserved across the bump.

## Validation
| | Before | After |
|---|---|---|
| lean v1→latest migration | ~567 B (defaults dump) | ~196 B (user config + version bump) |
| explicit non-default value | preserved | preserved |
| schema defaults | written to disk | merged at read time, absent from disk |

`scripts/run_tests.sh tests/hermes_cli/test_config.py tests/hermes_cli/test_setup.py` → 148 passed. Migration-adjacent suites (profiles, curator, migrate_xai, apply_profile_override) → 196 passed. ruff clean.

Relates to the config-bloat reports addressed piecemeal in #27354 / #40821 / #27539 / #53132; this makes the fix structural so the bug-class can't recur.