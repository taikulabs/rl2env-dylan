**feat(kanban): wire dispatcher to dispatch review agents from review column**

Salvages #23772 by @thewillhuang.

Adds `review` as a valid kanban task status and extends `dispatch_once` to monitor the review column as a second dispatch source (after the existing `ready` column). Review agents get the `sdlc-review` skill auto-loaded.

- Adds `review` to `VALID_STATUSES` (combined with main's `scheduled` state)
- Adds `claim_review_task()` — atomically transitions `review → running`
- Adds `has_spawnable_review()` — health telemetry mirror
- Extends `dispatch_once` with a review column dispatch loop after the ready loop

Resolved 2 stale-base conflicts. Adapted `claim_review_task` signature to main's `ttl_seconds: Optional[int] = None` convention so it composes cleanly with main's `_resolve_claim_ttl_seconds` helper. Authorship preserved via rebase merge.

## Validation
- 14 review-related tests pass.