**fix: use argparse entrypoint in top-level launcher**

The `./hermes` convenience script still used the legacy `fire.Fire(cli.main)` wrapper, which doesn't support subcommands (`gateway`, `cron`, `doctor`, etc.). The installed `hermes` command already uses `hermes_cli.main:main` via pyproject.toml — this aligns the launcher script.

Salvaged from PR #2009 by @gito369.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_launcher.py`