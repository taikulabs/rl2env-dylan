**feat(kanban): make worker log retention configurable**

Salvage of #25639 from @qWaitCrypto onto current main.

Adds two config knobs for kanban worker log rotation:
- `kanban.worker_log_rotate_bytes` (default 2 MiB — historical)
- `kanban.worker_log_backup_count` (default 1 — historical)

Defaults preserve the existing single-generation rotation behavior. Long-running workers can raise either value to keep more early failure evidence.

- Multi-generation rotation shifts `.log.1 → .log.2 → ...` up to `backup_count`.
- backup_count=0 unlinks the active log instead of rotating (advanced opt-out).

Original PR: #25639.

## Validation
- 3 new targeted tests passing; existing rotation tests still green (9/9 in the touched test selection).