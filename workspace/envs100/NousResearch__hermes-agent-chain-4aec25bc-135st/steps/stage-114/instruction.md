**feat(kanban): add respawn guard to block repeat worker storms**

Salvages #27484 by @fardoche6.

Adds a respawn guard that skips worker spawn for tasks where:
- a recent run already succeeded (`recent_success` — within guard window)
- the previous run hit a quota/auth error (`blocker_auth`, also auto-blocks the task)
- a recent task comment includes a GitHub PR URL (`active_pr`)

The guard prevents repeat worker storms on the same bug/task. Squashed the contributor's review-findings fixup commit (regex hardening, observability, auth coverage) into the base feature.

Resolved a small `DispatchResult` conflict alongside main's `stale` field; kept both. Authorship preserved via rebase merge.

## Validation
- 15 respawn-guard tests pass.