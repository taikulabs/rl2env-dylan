**feat(claw-migrate): harden OpenClaw import with plan-first apply, redaction, and pre-migration backup**

## Summary
`hermes claw migrate` now refuses to apply on conflicts, backs up `~/.hermes/` before any mutation, and redacts secrets in every report it writes. Four design patterns adopted from OpenClaw's reciprocal migrate-hermes importer (openclaw/, #72646) so both migration paths have the same safety posture.

## Changes
- `optional-skills/migration/openclaw-migration/scripts/openclaw_to_hermes.py`:
  - Engine-level `redact_migration_value()` — key-name markers (`apiKey`, `secret`, `token`, etc.) + value-shape patterns (`sk-*`, `ghp_*`, `xox*-`, `AIza*`, `Bearer *`) applied to every `report.json` / `summary.md` on disk and to `--json` stdout.
  - `_build_warnings()` + `_build_next_steps()` on `build_report()` — structured actionable guidance surfaces in both JSON and Markdown.
  - `_config_apply_blocked` flag + `run_if_selected()` guard — if a `config.yaml` write hits conflict/error mid-apply, later config-mutating options are marked `skipped` with reason `"blocked by earlier apply conflict"` rather than attempting partial writes.
  - `--json` flag — emits the redacted report on stdout for CI/automation.
  - `STATUS_*`, `REASON_*` constants and `ItemResult.sensitive: bool` — schema additions, backward-compatible (values match existing strings).
- `hermes_cli/claw.py`:
  - Plan-first apply: refuses to execute when the preview has any `conflict` items unless `--overwrite` is set. Previously the user could say "yes, proceed" and silently end up with everything skipped.
  - `_create_pre_migration_backup()` — one timestamped `~/.hermes/migration/pre-migration-backups/hermes-home-*.tar.gz` written before any mutation, excluding regenerable dirs (sessions, logs, cache, __pycache__, venvs, node_modules). Opt out with `--no-backup`.
  - `--preset full` no longer auto-enables `--migrate-secrets`. Users now have to opt in to secret import explicitly, matching OpenClaw's two-phase posture.
- `hermes_cli/main.py`: new `--no-backup` arg; updated `--preset`/`--overwrite`/`--migrate-secrets` help text.
- Docs: `website/docs/guides/migrate-from-openclaw.md` + `website/docs/reference/cli-commands.md` updated for preset-flip and `--no-backup`.

## Validation

| | Before | After |
|---|---|---|
| Tests (`tests/skills/test_openclaw_migration*.py` + `tests/hermes_cli/test_claw.py`) | 80 passing | 106 passing (+26 new: `test_openclaw_migration_hardening.py`) |
| `hermes claw migrate` with conflicts, no `--overwrite` | silently skips conflicts, says "migrated 0" | refuses to apply with actionable error |
| `report.json` / `summary.md` on disk | contains raw API keys if detected | all secrets → `[redacted]` |
| `--preset full` without `--migrate-secrets` | silently imports API keys | does not import secrets |
| Apply with existing `~/.hermes/` | no rollback point | tarball at `~/.hermes/migration/pre-migration-backups/hermes-home-*.tar.gz` |
| `--json` on script | not supported | emits redacted report; `--json` without `--execute` = safe plan-only |

Manual E2E against a fake `$HERMES_HOME` with real-shaped secrets confirmed: secrets never appear in stdout or on disk, `_cmd_migrate` refuses apply on conflicts, `--overwrite` proceeds past the guard and the backup tarball is created, `--no-backup` skips the archive.

Pre-existing `TestCmdCleanup` failures on `tests/hermes_cli/test_claw.py` are machine-dependent (detect real OpenClaw processes via `pgrep`) — confirmed present on `origin/main`, unrelated to this PR.