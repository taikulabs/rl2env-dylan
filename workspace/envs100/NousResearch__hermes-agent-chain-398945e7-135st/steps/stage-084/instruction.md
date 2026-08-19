**fix(curator): authoritative absorbed_into on delete + restore cron skill links on rollback**

## Summary
Two fixes for the curator + cron-link silent-failure class. .

1. **`absorbed_into` on skill delete** — curator reconciler stops guessing what "archived" means.
2. **Cron skill links are backed up with the snapshot and restored on rollback** — rolling back a curator run actually returns cron jobs to their pre-run state.

---

## 1. `absorbed_into` on skill delete

### Root cause
`_reconcile_classification` in `agent/curator.py` inferred consolidation vs pruning from two brittle signals: the curator's post-hoc YAML summary block, and a substring heuristic scanning sibling tool calls for the removed skill's name. Both miss in real consolidations — models forget the YAML under reasoning pressure, and the heuristic misses when the umbrella's patch content describes the absorbed behavior abstractly instead of literally naming the old slug. When both miss, the skill fell through to "no-evidence fallback" pruned, and #18253's cron-rewriter then dropped the cron ref entirely instead of mapping it to the umbrella. Same observable symptom as : `Skill(s) not found and skipped` on the next cron run.

### Changes
- `tools/skill_manager_tool.py` — `skill_manage(action='delete')` accepts `absorbed_into`:
  - `absorbed_into='<umbrella>'` → consolidated; target must exist on disk (validated)
  - `absorbed_into=''` → explicit prune, no forwarding target
  - missing → legacy path, reconciler falls through to heuristic/YAML (backward compat)
  - rejects `absorbed_into=<self>` and nonexistent targets
- `agent/curator.py` — new `_extract_absorbed_into_declarations()` pulls declarations off `llm_meta.tool_calls`. `_reconcile_classification` accepts `absorbed_declarations=` and treats it as **authoritative** — beats YAML block and heuristic. Curator prompt updated to require the arg on every delete.

---

## 2. Cron skill links through snapshot + rollback

### Root cause
`snapshot_skills()` captured the skills tree and `.curator_backups/…/skills.tar.gz` held it safely, but `~/.hermes/cron/jobs.json` was never captured. After a rollback, skills bounced back to disk but cron jobs still pointed at whatever umbrellas the curator had rewritten them to. User experience: "I rolled back but my cron jobs still use the merged skills."

### Changes
- `agent/curator_backup.py` — `snapshot_skills()` additionally copies `cron/jobs.json` as `cron-jobs.json` alongside the tarball. Manifest gains a `cron_jobs` block (`backed_up`, `jobs_count`, optional `reason`/`parse_warning`).
- `agent/curator_backup.py` — new `_restore_cron_skill_links(snapshot_dir)` reconciles backed-up skills into the live `jobs.json` **surgically**:
  - only `skills`/`skill` fields touched; schedule/prompt/timestamps/enabled/etc. are live state and preserved
  - matched by job `id`; jobs the user deleted after the snapshot are NOT resurrected; jobs the user created after are untouched
  - writes through `cron.jobs.save_jobs()` under the same `_jobs_file_lock` the scheduler uses — no race with `tick()`
  - failures here don't fail the overall rollback (skills tree is the core guarantee)
- `rollback()` calls `_restore_cron_skill_links` after the skills extract succeeds; the returned message summarizes the reconciliation ("cron links: N job(s) had skill links restored, M backed-up job(s) no longer exist").
- `hermes_cli/curator.py` — rollback confirm dialog shows cron-backup status from the manifest so the user knows what's about to happen.

---

## Validation
| | Before | After |
|---|---|---|
| Model consolidates, emits YAML, heuristic hits | ✓ | ✓ |
| **Model consolidates, forgets YAML, heuristic misses** | ✗ fell through to prune, cron ref dropped | ✓ `absorbed_into` declared → cron rewritten |
| Model truly prunes | inferred | explicit `absorbed_into=""` |
| Rollback restores skills tree | ✓ | ✓ |
| **Rollback restores cron skill links** | ✗ jobs still point at umbrellas | ✓ surgical restore; non-skill fields preserved |
| Rollback with pre-feature snapshot (no cron-jobs.json) | n/

…(truncated)