**fix: defer discord adapter annotations**

## Summary
- add postponed annotation evaluation to `gateway.platforms.discord`
- add a regression test proving the module still imports when `discord.py` is unavailable

## Why
The Discord adapter treats `discord.py` as optional, but the module still referenced types like `discord.Interaction` in annotations. On Python 3.11 those annotations were evaluated eagerly, so importing the module crashed with `AttributeError: 'NoneType' object has no attribute 'Interaction'` after the optional import fallback set `discord = None`.

This surfaced when running `python -m hermes_cli.main gateway restart` from the dev `.venv` on a machine where `discord.py` was not installed there.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/gateway/test_discord_imports.py`