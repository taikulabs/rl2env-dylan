**feat(cli): add `hermes send` to pipe script output to any messaging platform (salvage of #19631)**

## Summary
Salvage of #19631 — new `hermes send` CLI subcommand pipes text from shell scripts, CI hooks, post-commit hooks, watchdogs, etc. to any messaging platform Hermes is already configured for. Zero new platform code — thin wrapper over the existing `send_message_tool`.

Complements no-agent cron jobs (recurring) by covering the one-shot / externally-scheduled case.

## Examples
```bash
hermes send --to telegram "deploy finished"                    # home channel
echo "RAM 92%" | hermes send --to telegram:-1001234567890
hermes send --to discord:#ops --file report.md
hermes send --to slack:#eng --subject "[CI]" --file build.log
hermes send --to telegram:-1001234567890:17585 "threaded reply"
hermes send --list                                              # all targets
hermes send --list telegram                                     # platform filter
hermes send --list --json                                       # machine-readable
```

Exit codes: `0` ok, `1` delivery failure, `2` usage error.

## Home-channel behavior
`--to telegram` (platform only, no `:chat_id`) routes to the configured home channel via `send_message_tool`'s existing `config.get_home_channel(platform)` fallback. The `_load_hermes_env()` bootstrap bridges top-level `config.yaml` scalars (e.g. `TELEGRAM_HOME_CHANNEL` saved by `hermes config set`) into `os.environ` so the gateway config loader can resolve them from a fresh shell — covered by `test_load_hermes_env_bridges_config_yaml_scalars`.

## Salvage notes
Branch was 1,421 commits stale. One conflict in `automate-with-cron.md`: main added a tip pointing to no-agent cron between this PR's branch and now; PR was adding a tip pointing to `hermes send`. Merged both into a single "two zero-token options" callout so the docs cover the recurring (cron) vs one-shot (`hermes send`) split.

## Changes
- `hermes_cli/send_cmd.py` (+~300): the CLI module. Argparse setup, body-source precedence (positional > `--file` > stdin), `--list` formatter, env bootstrap.
- `hermes_cli/main.py` (+~4): subparser registration alongside other messaging commands.
- `tests/hermes_cli/test_send_cmd.py` (+~200): 20 tests — happy paths (positional, stdin, --file, --subject, --json, --quiet), error paths (missing --to, missing body, file not found), --list (human / json / filter / unknown platform), env loader (bridge + no-override + missing files), registrar contract.
- `website/docs/guides/pipe-script-output.md` (+full guide): watchdog pattern, CI notifications, cron piping, scripting with `--json` / `--quiet`. Comparison table vs raw curl, no-agent cron, and the `send_message` agent tool.
- `website/docs/guides/automate-with-cron.md`: merged tip box.
- `website/docs/developer-guide/gateway-internals.md`: cross-link from delivery-path section.

## Validation
| | Result |
|---|---|
| `tests/hermes_cli/test_send_cmd.py` | 20/20 |
| `hermes send --help` | Renders cleanly |
| Live smoke (from PR author) | Delivered to Telegram home channel from a fresh shell |

## Compatibility
- No new dependencies.
- No config migration.
- No changes to existing commands or tools.

## Source
Originally scouted in #19631.