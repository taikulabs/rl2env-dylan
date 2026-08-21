**fix(curator): rewrite cron job skill refs after consolidation**

## Summary
After a curator consolidation run, cron jobs whose `skills[]` referenced a consolidated or pruned skill now get auto-rewritten in-place so they keep loading the right instructions on their next run.

Reported by @tombielecki: "If a cron job is used to schedule the execution of a skill, the curator consolidation doesn't update those references/invocations so the jobs might silently fail."

Root cause: the curator archives the old skill directory but has no knowledge of `~/.hermes/cron/jobs.json`. The scheduler's per-skill `skill_view` call logs a warning and skips the missing skill, but the job still runs — without the instructions it was scheduled to follow.

## Changes
- `cron/jobs.py`: new `rewrite_skill_refs(consolidated, pruned)` — loads jobs under the in-process lock, maps consolidated names → umbrella target (dedup when umbrella already present), drops pruned names, saves atomically via the existing `save_jobs` path. Returns a per-job report.
- `agent/curator.py`: `_write_run_report` calls it after classification. Best-effort try/except — a cron-side failure never breaks the curator. Rewrite summary is recorded in `run.json` (`counts.cron_jobs_rewritten` + full `cron_rewrites` payload), a separate `cron_rewrites.json` when jobs were touched, and a dedicated section in `REPORT.md`.
- Tests: 16 unit tests for the rewrite function (consolidation, pruning, dedupe, mixed, persistence, legacy `skill` field) + 3 integration tests through `_write_run_report`.

## Validation
|  | Before | After |
|---|---|---|
| Cron ref to consolidated skill | Silent skip at runtime (log warning + agent notice, job runs without instructions) | Auto-rewritten to umbrella |
| Cron ref to pruned skill | Same silent skip | Dropped, surfaced in report |
| Umbrella already in job's list | Would duplicate after rewrite | Dedupes to single entry |
| Unrelated cron jobs | Untouched | Untouched (verified) |
| Curator run with no consolidations | n/a | No cron_rewrites.json written; no section in md |
| Legacy `skill` (single) field | Not updated | Realigned via `_apply_skill_fields` |

E2E run with 4 real jobs + real `_write_run_report` + real disk I/O:
- `sales-analyzer-job` `[sales-analyzer]` → `[business-metrics]`
- `deploy-check-job` `[deploy-check, unrelated]` → `[deployment-umbrella, unrelated]`
- `stale-skill-job` `[old-stale-thing]` → `[]` (pruned, dropped)
- Untouched job `[keep-me-alone]` → unchanged

Targeted test run: 124/124 passed (`tests/agent/test_curator*.py` + `tests/cron/test_cron_script.py` + `tests/cron/test_rewrite_skill_refs.py`).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/agent/test_curator_reports.py`
- `tests/cron/test_rewrite_skill_refs.py`