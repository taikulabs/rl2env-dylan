**fix(update): prompt before resetting working tree on stash conflicts**

## Summary

When `hermes update` stashes local changes and the restore hits conflicts, the previous behavior silently ran `git reset --hard HEAD`. Users could lose their working tree state without realizing it.

Now the conflict handler:
- Lists the specific conflicted files
- Reassures the user their stash is preserved
- **Asks before resetting** (in interactive mode)
- Auto-resets in non-interactive mode (`prompt_user=False`)
- If the user declines, leaves the working tree as-is with guidance on manual resolution

Inspired by the autostash improvements in PR #2370 (which bundled this with an unrelated prompt_caching change).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_update_autostash.py`