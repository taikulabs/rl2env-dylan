**feat(backup): exclude checkpoints/ from backups**

## Summary
`hermes backup` and the pre-update backup hook now skip `<HERMES_HOME>/checkpoints/`. Checkpoints are session-local trajectory caches — hash-keyed, regenerated per session, and wouldn't port to another machine anyway. On a heavy install this was multi-GB of dead weight in every zip.

## Changes
- `hermes_cli/backup.py`: `checkpoints` added to `_EXCLUDED_DIRS` alongside `backups`, `.git`, `__pycache__`, `node_modules`, `hermes-agent`
- `tests/hermes_cli/test_backup.py`: new `test_excludes_checkpoints` + `test_excludes_backups_dir` regression test for the sibling exclusion

## Validation
| | Before | After |
|---|---|---|
| `checkpoints/<hash>/trajectory.json` in zip | included | excluded |
| `tests/hermes_cli/test_backup.py` | 83 passed | 85 passed |

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_backup.py`