**fix(curator): defer first run and add --dry-run preview**

## Summary
Curator no longer auto-mutates a fresh skill library on the first gateway tick after `hermes update`. First observation seeds `last_run_at='now'` and defers the first real pass by one full `interval_hours` (7 days by default), matching the original design intent. `hermes curator run --dry-run` previews what a pass would do without touching anything.

Root cause: `should_run_now()` returned `True` when `last_run_at` was `None`, so the gateway cron ticker (`maybe_run_curator(idle_for_seconds=inf, …)`) fired immediately on fresh installs. Combined with the binary 'agent-created' provenance model (anything not bundled and not hub-installed), this consolidated hand-authored user workflow skills without consent — exactly what #18373 reported.

## Changes
- `agent/curator.py`: `should_run_now()` seeds state and returns `False` on first observation. `run_curator_review()` accepts `dry_run=True` — skips `apply_automatic_transitions`, prepends a DRY-RUN banner to the LLM prompt ("DO NOT call skill_manage / terminal mv"), and does not advance `last_run_at` or `run_count`. New `CURATOR_DRY_RUN_BANNER` constant.
- `hermes_cli/curator.py`: `hermes curator run --dry-run` flag wired through. Dry-run output is labeled and instructs the user how to follow up.
- `hermes_cli/main.py`: `_print_curator_first_run_notice()` prints a short heads-up after `hermes update` — only when curator is enabled AND has never run. Silent otherwise. Called from both `cmd_update` paths.
- `tests/agent/test_curator.py`: old `test_first_run_always_eligible` replaced with `test_first_run_defers` (same fixture, inverted expectation). New `test_maybe_run_curator_defers_on_fresh_install` covers the gateway tick path. Three dry-run tests: state-advance suppression, prompt-banner injection, `apply_automatic_transitions` skipping.
- Docs: `website/docs/user-guide/features/curator.md` gets an `:::info First-run behavior` admonition and a `:::warning` spelling out that hand-written `SKILL.md` files share the 'agent-created' bucket. `website/docs/reference/cli-commands.md` adds the `--dry-run` row.

## Validation
| | Before | After |
|---|---|---|
| `maybe_run_curator(idle=inf)` on fresh install | fires Curator, archives user skills | returns `None`, seeds state, silent |
| `should_run_now()` when `last_run_at=None` | `True` | `False` (seeds and defers) |
| `hermes curator run --dry-run` | n/a (flag did not exist) | writes REPORT.md, no filesystem mutation, does not bump `last_run_at` |
| `hermes update` output on fresh install | silent | short `ℹ Skill curator` notice with preview command |
| Curator tests | 75 passing | 79 passing (4 new, 1 rewritten) |

E2E: ran the exact gateway call (`maybe_run_curator(idle_for_seconds=float('inf'))`) against an isolated temp HERMES_HOME with a user-authored SKILL.md — confirmed the skill survives the first two ticks, `.archive` is never created, `should_run_now()` opens the gate only after 8 days, and a dry-run pass produces a banner-carrying prompt with no state advance.

.