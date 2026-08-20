**feat(plugins): add ctx.profile_name for session-agnostic profile access**

## Summary
Plugins can now read the active profile name from `PluginContext` via `ctx.profile_name`, in any execution context.

Previously there was no API for this. The workaround seen in the community — reaching into `ctx._manager._cli_ref` — only works in an interactive CLI session: `_cli_ref` is set exactly once (`cli.py`, in the interactive `run()` loop) and is `None` in the gateway and in **kanban-spawned worker sessions** (`hermes -p <profile> chat -q ...`), which is exactly where per-profile awareness matters most.

## Changes
- `hermes_cli/plugins.py`: add `PluginContext.profile_name` property, wrapping `hermes_cli.profiles.get_active_profile_name()` (derives from `HERMES_HOME`, no `_cli_ref` dependency).
- `tests/hermes_cli/test_plugins.py`: cover default profile, named profile, and the `_cli_ref is None` (worker) case.

## Validation
| Context | `_cli_ref` | `ctx.profile_name` |
|---|---|---|
| Interactive CLI | set | resolves |
| Gateway | None | resolves |
| Kanban worker (`chat -q`) | None | resolves (E2E verified → `kanban-worker`) |

89/89 tests pass in `tests/hermes_cli/test_plugins.py`. E2E-verified with real imports against a temp profile-scoped `HERMES_HOME` and `_cli_ref = None`.

Reported by @Smithangshu on Discord.

## Infographic

![ctx-profile-name](https://v3b.fal.media/files/b/0a9f38b5/Z-FH7D73uwLCE7S2rQsB8_hZQZoOH8.png)

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_plugins.py`