**fix(plugins): await async slash-command handlers in CLI and TUI dispatch**

Salvage of #17963 (@hharry11) onto current main, plus a 30s timeout on the threaded-await path.

## Summary
Plugin slash commands can be declared with `async def handler(args)` (documented in `PluginContext.register_command`), but only the gateway was awaiting them. CLI `process_command()` and TUI `command.dispatch` returned the coroutine object without running the body. This PR adds a shared `resolve_plugin_command_result()` helper in `hermes_cli/plugins.py` and wires both dispatch sites through it.

## Changes
- `hermes_cli/plugins.py`: new `resolve_plugin_command_result()` — passthrough for sync results, `asyncio.run()` when no loop is active, threaded `asyncio.run()` when a loop is running.
- `cli.py`: CLI plugin slash command dispatch goes through the helper.
- `tui_gateway/server.py`: `command.dispatch` plugin branch goes through the helper.
- Follow-up commit: 30s timeout on the threaded-await `Event.wait()` so a hung async handler cannot wedge the terminal. Raises `TimeoutError` on expiry.
- Tests: 4 from the original PR + 1 new timeout regression test.

## Validation
```
scripts/run_tests.sh tests/hermes_cli/test_plugins.py::TestPluginCommandResultResolution \
                     tests/tui_gateway/test_protocol.py::test_command_dispatch_awaits_async_plugin_handler
# 5 passed
```

. Original author @hharry11 preserved via cherry-pick; follow-up timeout commit is ours.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_plugins.py`