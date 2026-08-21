**fix(tools): prevent git argument injection and path traversal in checkpoint manager**

## Summary

Salvage of #7919 by @Dusk1e — cherry-picked onto current main with their authorship preserved.

Adds input validation to `CheckpointManager.restore()` and `diff()` to prevent:

1. **Git argument injection** — crafted commit hashes starting with `-` (e.g. `--patch`, `--exec`) get interpreted as git flags when passed to `git cat-file`, `git diff`, `git checkout` before the `--` separator
2. **Path traversal** — `file_path` in `restore()` allowed absolute paths (`/etc/passwd`) and relative escapes (`../../../etc/passwd`)

### Changes

- `_validate_commit_hash()` — enforces 4-64 hex chars, rejects leading `-`
- `_validate_file_path()` — rejects absolute paths, uses `Path.resolve()` + `relative_to()` for containment check
- Validation applied at entry points of both `restore()` and `diff()`
- `TestSecurity` test suite covering argument injection, invalid hex, path traversal, and valid path acceptance

### Test results

```
41 passed in 1.13s
```

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_checkpoint_manager.py`