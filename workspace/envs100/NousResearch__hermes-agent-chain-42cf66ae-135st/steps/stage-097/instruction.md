**fix(update): clarify manual autostash cleanup**

## Summary
- add shared guidance for cleaning up a restored autostash without reapplying it twice
- tell users to check On branch hermes/hermes-8bb24bf8
Your branch is up to date with 'origin/hermes/hermes-8bb24bf8'.

nothing to commit, working tree clean first and list stash entries with commit hashes and subjects
- cover the new guidance in update autostash tests

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_autostash.py`