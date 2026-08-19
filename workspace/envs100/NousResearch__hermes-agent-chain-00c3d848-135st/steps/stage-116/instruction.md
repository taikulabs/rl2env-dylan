**fix(profiles): migrate Honcho host on rename**

Salvage of #16724 onto current main. Cherry-picked helix4u's commit; authorship preserved via rebase-merge.

## Summary
`hermes profile rename old new` now migrates `hosts.hermes.old` → `hosts.hermes.new` in honcho.json, preserving `aiPeer` so memory identity survives the rename.

Reported on Discord by nekopep: after renaming `ssi_health` → `heimdall`, the stale `hosts.hermes.ssi_health` block was orphaned and the renamed profile couldn't find its Honcho config.

## Changes
- `hermes_cli/profiles.py`: new `_migrate_honcho_profile_host()`, called as step 3 in `rename_profile()`. Walks profile-local `honcho.json`, `~/.hermes/honcho.json`, and `~/.honcho/config.json` (matches `resolve_config_path()`'s read order). Skips with a warning if the destination host key already exists.
- `tests/hermes_cli/test_profiles.py`: 3 new tests — host rename preserves `aiPeer`, pins `aiPeer` when absent, refuses to overwrite an existing destination host.

## Validation
`tests/hermes_cli/test_profiles.py`: 92/92 pass. `tests/honcho_plugin/`: 266/266 pass.

.