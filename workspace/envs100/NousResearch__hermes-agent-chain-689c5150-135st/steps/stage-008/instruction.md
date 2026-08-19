**perf(ssh,modal): bulk file sync via tar pipe and tar/base64 archive**

## Summary

Salvage of #7558 by @kshitijk4poor onto current main. Contributor commits cherry-picked with authorship preserved.

- **SSH**: `tar -ch | ssh tar x` single-stream bulk upload with symlink staging, ControlMaster reuse, full error/timeout handling
- **Modal**: in-memory tar.gz streamed through `proc.stdin` in 1MB chunks, avoiding Modal SDK's 64KB `ARG_MAX_BYTES` limit
- **Shared helpers**: `quoted_mkdir_command()` and `unique_parent_dirs()` extracted to `file_sync.py`
- **Daytona**: migrated to use shared helpers (was duplicating inline)

### Follow-up fixes (second commit)
- **Critical**: Modal bulk upload embedded the entire base64 payload (~4.3MB for 580 files) in the `bash -c` command string, exceeding Modal SDK's 64KB `ARG_MAX_BYTES` exec-arg limit. Rewrote both `_modal_upload` and `_modal_bulk_upload` to pipe through `proc.stdin` with chunked writes.
- Modal single-file upload now checks exit code (was silently swallowing failures).
- Removed what-narrating comments; kept WHY comments (symlink staging rationale, SIGPIPE, deadlock avoidance).
- Daytona `_daytona_bulk_upload` now uses `unique_parent_dirs()` + `quoted_mkdir_command()` instead of inlined duplicates.

### Backend status

| Backend | Upload method | Bulk support | Status |
|---------|--------------|--------------|--------|
| Daytona | SDK `upload_files()` | Done | Already merged |
| SSH | `tar -ch \| ssh tar x` | Done (this PR) | **New** |
| Modal | `tar+base64 \| proc.stdin` | Done (this PR) | **New** |
| Docker | Bind mount | N/A | No sync needed |
| Singularity | Bind mount | N/A | No sync needed |

44 tests passing (21 SSH, 9 Modal, 14 file_sync).

Supersedes #7558