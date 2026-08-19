**feat(update): add --yes/-y to skip interactive prompts**

## Summary
`hermes update` now accepts `--yes`/`-y` to auto-answer its two interactive `[Y/n]` prompts, matching the existing `hermes uninstall --yes` convention. Reported by @murelux.

## Changes
- `hermes_cli/main.py`: new `--yes`/`-y` flag on the `update` subparser; under the flag, both interactive prompts are auto-answered:
  - **Config-migrate prompt** → auto-yes, runs `migrate_config(interactive=False)` so new config fields land automatically but API-key prompts are skipped (user runs `hermes config migrate` later for those). Matches gateway-mode semantics already in place.
  - **Autostash restore prompt** → auto-yes, `git stash apply` runs automatically.
- `tests/hermes_cli/test_update_yes_flag.py`: 3 new tests covering (a) `--yes` skips the config-migrate prompt and calls `migrate_config` with `interactive=False`, (b) regression guard that without `--yes` the TTY prompt path still fires, (c) `--yes` passes `prompt_user=False` into `_restore_stashed_changes`.

## Validation
| | Before | After |
|---|---|---|
| `hermes update -y` (new config fields) | prompts for Y/N | auto-yes, applies additions, skips API-key prompts |
| `hermes update -y` (dirty tree) | prompts to restore stash | auto-restores stash |
| `hermes update` (no flag) | unchanged | unchanged |
| `tests/hermes_cli/test_update*` (93 tests) | pass | pass |
| New `test_update_yes_flag.py` (3 tests) | — | pass |