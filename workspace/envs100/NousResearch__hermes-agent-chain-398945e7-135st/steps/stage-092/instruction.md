**fix(discord): /reload-skills now refreshes the /skill autocomplete live**

## Summary

`/reload-skills` was a no-op for Discord's `/skill` autocomplete.

`_register_skill_group` captured the skill catalog in **closure** variables (`entries`, `skill_lookup`) so the single `tree.add_command` at startup owned the only live copy. The closure is never re-entered, so rescanning disk and refreshing the in-process `_skill_commands` registry couldn't propagate to the Discord picker. Observable behavior:

- Skill added at runtime → invisible in `/skill` autocomplete until the gateway restarts.
- Skill removed at runtime → stale autocomplete entry remains; clicking it returns *"Unknown skill"*.

## Fix

Purely a dataflow change on the Discord adapter:

- Promote `entries` / `skill_lookup` to instance attrs (`_skill_entries`, `_skill_lookup`) so the autocomplete + handler callbacks read live state.
- Factor the collector-driven rebuild into `_refresh_skill_catalog_state()`.
- Expose a public `refresh_skill_group()` that re-runs the helper and is safe to call at any point after initial registration.

Gateway-side, `_handle_reload_skills_command` now walks `self.adapters` and calls `refresh_skill_group()` on any adapter that exposes it. Both sync and async implementations are supported; adapters that don't override it (Telegram BotCommand menu, Slack subcommand map, etc.) are silently skipped — the in-process `reload_skills()` call above already covers them.

No `tree.sync()` is needed — Discord fetches autocomplete options dynamically on every keystroke, so mutating the instance state is enough. This also sidesteps Discord's per-app command-bucket rate limit (~5 writes / 20 s), which has caused outages in the past.

## Tests

`tests/gateway/test_reload_skills_discord_resync.py` — five cases:

1. `test_refresh_repopulates_entries_after_catalog_change` — add + remove shows up immediately.
2. `test_refresh_sorts_entries_alphabetically` — order stays stable across refreshes.
3. `test_refresh_handles_collector_exception_gracefully` — broken collector doesn't crash the gateway.
4. `test_refresh_catalog_state_populates_instance_attrs` — the shared helper populates `self._skill_entries` / `self._skill_lookup`.
5. `test_orchestrator_calls_refresh_skill_group_on_every_adapter` — gateway invokes refresh on sync + async adapters and skips no-op adapters.

All pass; 148 surrounding Discord + hermes_cli tests still pass.

## Related

Third in a series triaging "Discord /skill commands not finding a skill":
- #18745 — drop legacy 25×25 caps + complete #18741's external_dirs fix for the live collector.
- #18753 — match disabled/optional skills by frontmatter slug, not directory name.
- **this PR** — `/reload-skills` actually refreshes the live Discord autocomplete.