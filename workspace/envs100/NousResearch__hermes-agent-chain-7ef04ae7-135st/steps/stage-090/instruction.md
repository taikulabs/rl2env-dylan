**fix(installer): recover bootstrap when managed git clone diverged**

## Summary
- Bootstrap/desktop updates failed at the `repository` stage when `~/.hermes/hermes-agent` had diverged from `origin/main` (`git pull --ff-only` exit 128)
- `hermes update` already recovers by resetting to `origin/$BRANCH`; `install.sh` and `install.ps1` did not
- Add the same ff-only → `reset --hard origin/$BRANCH` fallback to both installer scripts

. Supersedes #53363 by also covering `install.ps1` (Windows bootstrap).

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/test_install_diverged_update.py`