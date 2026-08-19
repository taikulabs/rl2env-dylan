**fix: preserve symlinks during atomic file writes**

Atomic writes no longer detach symlinks from their tracked targets. Managed deployments that symlink `~/.hermes/config.yaml`, `SOUL.md`, `auth.json`, `.env`, sessions, cron state, etc. to a git-tracked profile package or dotfiles repo now stay linked through every write path.

Builds on #16777 by @vominh1919.

## Changes
- **utils.py**: new shared `atomic_replace(tmp, target)` helper that resolves symlinks through `os.path.realpath` before `os.replace`. `atomic_json_write` / `atomic_yaml_write` call it instead of inlining the guard.
- **16 files**: every `os.replace()` call site in the codebase migrated to `atomic_replace()`. #16777 fixed 9 sites; this PR widens the same fix to the 10+ sibling sites the original missed:
  - agent: `google_oauth.py`, `nous_rate_guard.py`, `shell_hooks.py`
  - cron: `jobs.py`
  - gateway: `pairing.py`, `session.py`, `platforms/telegram.py`
  - hermes_cli: `auth.py`, `config.py`, `debug.py`, `env_loader.py`, `model_catalog.py`, `webhook.py`
  - tools: `memory_tool.py`, `skill_manager_tool.py`, `skills_sync.py`

Zero bare `os.replace()` calls remain in the codebase outside the helper itself.

## Root cause
`os.replace(tmp, target)` atomically swaps `tmp` into place at `target`. When `target` is a symlink, the symlink itself is replaced with a regular file, detaching the user's source-of-truth silently. The helper resolves through `realpath` first so the real file is overwritten in-place while the symlink survives.

## Validation
| | Before | After |
|---|---|---|
| symlinked config.yaml after `save_config` | regular file | symlink preserved, real file updated |
| symlinked .env after `save_env_value` | regular file | symlink preserved, real file updated |
| first-time creates | worked | worked |
| plain files | worked | worked |
| broken symlinks | dangling link replaced with regular file | symlink preserved, real target created |

- `tests/test_atomic_replace_symlinks.py`: 8 new tests covering the helper, `atomic_json_write`, `atomic_yaml_write`, permission preservation, and the broken-symlink edge case — all pass.
- 488 tests across affected subsystems (memory, skill manager, cron, config, env_loader, session) pass.
- E2E: real `save_config` + `save_env_value` against a symlinked HERMES_HOME → symlinks survive, tracked source files updated in place.
- All 16 modified modules import cleanly (no circular-import regressions).

Supersedes #16777 (vominh1919's commit cherry-picked, authorship preserved).