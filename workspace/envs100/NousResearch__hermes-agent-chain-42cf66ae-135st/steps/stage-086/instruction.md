**fix: harden .worktreeinclude path containment**

## Summary
- cherry-pick the substantive `.worktreeinclude` containment fix from #1267 so worktree includes cannot escape the repo or worktree roots
- harden the follow-up check to use `Path.relative_to()` semantics and explicitly cover symlink escapes as well as `../` traversal
- replace the replayed test logic from the cherry-picked PR with real integration tests that exercise `cli._setup_worktree()` directly