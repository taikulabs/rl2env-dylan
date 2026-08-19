**fix(gateway): hide required-arg commands from Telegram menu**

Salvage of #19343 by @mrbob-git onto current main.

## Summary
Telegram BotCommand menu selections send only the bare `/command`. Commands like `/background`, `/queue`, and `/steer` require a prompt argument, so listing them in the native Telegram menu lets users execute them incomplete. Skip commands whose `args_hint` starts with `<` from the menu; they remain dispatchable if typed manually.

## Changes
- hermes_cli/commands.py: `_requires_argument()` helper + filter in `telegram_bot_commands()` (+11/-2)
- tests: regression covering `/background`, `/queue`, `/steer` exclusion
- scripts/release.py: AUTHOR_MAP entry for @mrbob-git

## Validation
scripts/run_tests.sh tests/hermes_cli/test_commands.py → 141 passed

Original PR: #19343