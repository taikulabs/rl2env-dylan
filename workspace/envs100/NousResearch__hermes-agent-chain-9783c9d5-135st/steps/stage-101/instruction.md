**fix: use argparse entrypoint in top-level launcher**

The `./hermes` convenience script still used the legacy `fire.Fire(cli.main)` wrapper, which doesn't support subcommands (`gateway`, `cron`, `doctor`, etc.). The installed `hermes` command already uses `hermes_cli.main:main` via pyproject.toml — this aligns the launcher script.

Salvaged from PR #2009 by @gito369.