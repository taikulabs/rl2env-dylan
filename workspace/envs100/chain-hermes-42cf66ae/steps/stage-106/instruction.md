**fix(config): reload .env over stale shell overrides**

## Summary
- load Hermes env files through a shared helper that lets `~/.hermes/.env` override stale shell-exported values on restart
- preserve user env over project fallback while still letting the project `.env` fill missing values in dev setups
- wire the shared loader into the main startup entrypoints and add regression coverage for the reported stale-BASE_URL/provider case

## Root cause
I reproduced the issue directly on current main:
- shell had stale `OPENAI_BASE_URL=https://old.example/v1`
- `~/.hermes/.env` contained `OPENAI_BASE_URL=https://new.example/v1` and `HERMES_INFERENCE_PROVIDER=custom`
- importing `hermes_cli.main` left the old shell values in place because the startup dotenv loads were using the default `override=False`

That meant editing `.env` and restarting Hermes could still leave the process pinned to old model/provider/base_url settings if those vars were already exported in the parent shell.

## Graded tests

This stage is graded by these tests (already in your workspace at these paths; they were overwritten with the project copy when the stage opened, so edit the source, not the tests):

- `tests/hermes_cli/test_env_loader.py`