**feat: show estimated tool token context in hermes tools checklist**

## Summary

Salvage of PR #1742. Shows a live token estimate at the bottom of the `hermes tools` curses checklist that updates in real-time as toolsets are toggled on/off.

Example: `Est. tool context: ~8.8k tokens`

## Changes

- **tools/registry.py** — Add `get_schema(name)` for raw schema introspection
- **hermes_cli/curses_ui.py** — Add generic `status_fn` callback to curses checklist + numbered fallback
- **hermes_cli/tools_config.py** — Token estimation via tiktoken with caching, deduplication via `resolve_toolset()`, graceful degradation
- **tests/** — 12 new tests covering estimation, caching, degradation, dedup, curses fallback, registry

## Fix applied during salvage

The original PR built `ts_keys` from `CONFIGURABLE_TOOLSETS`, but the checklist uses `_get_effective_configurable_toolsets()` which includes plugin toolsets. Fixed to use `effective` so indices match when plugins are present (prevents IndexError).

## Verified

- All 12 new tests pass
- 4251 tests pass across hermes_cli (754), tools (1866), gateway (1631)
- Live tested in tmux PTY — token count displays correctly, updates in real-time when toggling toolsets