**fix: expand environment blocklist for terminal isolation**

## Summary
- 
- add regression coverage for the newly blocked non-registry provider env vars so they are both present in the blocklist and stripped from subprocess environments

## Contributor credit
Salvages PR #1384 by cherry-picking the contributor commit onto current main with authorship preserved, plus a small current-main test follow-up.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/tools/test_local_env_blocklist.py`