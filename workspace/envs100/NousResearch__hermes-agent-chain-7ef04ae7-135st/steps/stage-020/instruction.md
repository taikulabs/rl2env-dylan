**fix(windows): repair missing console script launchers**

## Summary
- Supersedes #52940 and #53203 with a single branch that preserves both contributors' authored commits.
- Verifies declared `[project.scripts]` launchers after Windows installs, including the primary successful editable-install path where #52931 reproduces.
- Reinstalls entry points when launchers are missing and broadens Windows quarantine coverage to all declared console scripts plus the legacy gateway shim.

## Authorship
- HexLab98's base repair and test commits were cherry-picked with original authorship preserved.
- Gille's follow-up placement/quarantine fix was applied as a separate authored commit.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_verify_console_scripts.py`