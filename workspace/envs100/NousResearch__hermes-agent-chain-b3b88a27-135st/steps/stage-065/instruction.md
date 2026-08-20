**feat(update): warn about legacy hermes.service units during hermes update**

## Summary
`hermes update` now flags legacy pre-rename `hermes.service` units so users who still have them learn about the flap-loop risk and the migration command without having to stumble into `hermes gateway status` or a fresh install.

.

## Changes
- `hermes_cli/main.py` `cmd_update`: after the gateway-restart block and before the final tips, call `has_legacy_hermes_units()` and print the list + `hermes gateway migrate-legacy` command.
- Systemd-gated (rename is Linux-only — macOS launchd didn't have a rename).
- Non-blocking: prints, never prompts — safe for `hermes update --gateway` non-interactive path.

## Profile safety
Reuses `_find_legacy_hermes_units()` from #11909 — explicit allowlist, no globs. `hermes-gateway-coder.service` etc. are never flagged. Verified by `test_update_does_not_flag_profile_units`.

## Validation
| | Before | After |
|---|---|---|
| `hermes update` with orphan `hermes.service` | silent | prints warning + migrate command |
| `hermes update` with only profile units | silent | silent (no false positive) |
| `hermes update` on macOS/Termux | silent | silent (systemd-gated) |

5 new tests in `TestCmdUpdateLegacyGatewayWarning`, all passing. Full `test_update_gateway_restart.py` suite: 39/39 passing.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_gateway_restart.py`