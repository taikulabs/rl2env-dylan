**feat(plugins): add slash command registration for plugins**

## Summary

Plugins can now register slash commands via `ctx.register_command()`. Commands automatically integrate with the full command infrastructure — `/help`, tab autocomplete, Telegram bot menu, Slack subcommand mapping, and gateway dispatch.

### Example

```python
def register(ctx):
    ctx.register_command(
        name="greet",
        handler=lambda args: f"Hello, {args or 'world'}!",
        description="Greet someone",
        args_hint="[name]",
        aliases=("hi",),
    )
```

### Handler contract
- Receives `args: str` (everything after the command name)
- Returns `str | None` (response to display, or None for silent)
- Async handlers supported in gateway context

### Changes
- `hermes_cli/commands.py`: `register_plugin_command()` + `rebuild_lookups()` to refresh derived dicts after plugins load
- `hermes_cli/plugins.py`: `register_command()` on `PluginContext`, `_plugin_commands` on `PluginManager`, `commands_registered` on `LoadedPlugin`
- `cli.py`: dispatch plugin commands in `process_command()` before skill commands
- `gateway/run.py`: dispatch plugin commands before skill commands (with async handler support)
- `tests/test_plugins.py`: 5 new tests covering registration, help integration, tracking, handler dispatch, and gateway known commands
- Docs: updated plugins feature page + build guide

### Verification
- 5758 tests pass (5 new plugin command tests + all existing)
- Plugin commands appear under a new "Plugins" category in `/help`