**fix: auto-register all gateway commands as Discord slash commands**

## Summary

Discord's `_register_slash_commands()` had a hardcoded list of ~27 commands, while `COMMAND_REGISTRY` defines 34+ gateway-available commands. This caused commands like `/debug`, `/branch`, `/yolo`, `/fast`, `/reload`, `/profile`, `/rollback`, `/snapshot`, and `/commands` to be invisible in Discord's `/` autocomplete — users couldn't discover or use them natively.

**Root cause:** Telegram and Slack already derive their command menus dynamically from `COMMAND_REGISTRY` (via `telegram_bot_commands()` and `slack_subcommand_map()`). Discord was the only platform with a manually maintained hardcoded list.

## Changes

**`gateway/platforms/discord.py`**
- Added a dynamic catch-all loop at the end of `_register_slash_commands()` that:
  1. Collects already-registered command names from the tree
  2. Iterates `COMMAND_REGISTRY` filtered by `_is_gateway_available()`
  3. Auto-registers missing commands using `discord.app_commands.Command()`
  4. Commands with `args_hint` get an optional string `args` parameter
  5. Parameterless commands get a simple callback
- Uses factory functions to avoid closure variable capture bugs
- Respects `gateway_config_gate` (e.g. `/verbose` only appears when config gate is enabled)
- Silently skips registration failures (name conflicts, etc.)

**Commands now auto-registered on Discord (9):**
| Command | Args | Description |
|---------|------|-------------|
| `/debug` | — | Upload debug report |
| `/branch` | `[name]` | Branch the current session |
| `/rollback` | `[number]` | List or restore checkpoints |
| `/snapshot` | `[create\|restore\|prune]` | State snapshots |
| `/profile` | — | Show active profile |
| `/yolo` | — | Toggle YOLO mode |
| `/fast` | `[normal\|fast\|status]` | Toggle fast mode |
| `/reload` | — | Reload .env variables |
| `/commands` | `[page]` | Browse all commands |

**Future-proof:** Any new commands added to `COMMAND_REGISTRY` will automatically appear on Discord without needing a manual entry.

## Tests
- 3 new tests for auto-registration: presence check, parameterless dispatch, args dispatch
- All 24 Discord slash command tests pass
- All 158 related tests pass (commands, Discord connect/imports/controls/skills)

Reported by @spoofydude on Discord — `/debug` wasn't available in the slash command picker.