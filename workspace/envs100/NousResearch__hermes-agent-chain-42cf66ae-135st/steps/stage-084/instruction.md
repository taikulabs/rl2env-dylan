**fix: harden .worktreeinclude path containment**

## Summary
- 
- harden the follow-up check to use `Path.relative_to()` semantics and explicitly cover symlink escapes as well as `../` traversal
- replace the replayed test logic from the cherry-picked PR with real integration tests that exercise `cli._setup_worktree()` directly

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_worktree_security.py`