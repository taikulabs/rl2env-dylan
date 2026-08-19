**fix: load trajectory compressor credentials from HERMES_HOME/.env**

## Summary

Fix `trajectory_compressor.py` so it loads credentials from the standard Hermes user config location: `HERMES_HOME/.env`.

Before this change, trajectory compression could fail when `OPENROUTER_API_KEY` was defined only in `HERMES_HOME/.env`, because the module relied on plain `load_dotenv()` during import instead of Hermes' shared env-loading behavior.

## Root Cause

`trajectory_compressor.py` called raw `load_dotenv()` at import time.

That only searches for `.env` using normal dotenv discovery rules (for example, the current working directory chain). It does **not** reliably load the standard Hermes config location at `HERMES_HOME/.env`.

As a result, users following the normal Hermes setup pattern could have a valid API key in `HERMES_HOME/.env`, while trajectory compression still behaved as if the key was missing.

## Repro

1. Create a temporary `HERMES_HOME`
2. Write `OPENROUTER_API_KEY=from-hermes-home` to `HERMES_HOME/.env`
3. Clear `OPENROUTER_API_KEY` from the process environment
4. Import `trajectory_compressor.py`
5. Check `os.getenv("OPENROUTER_API_KEY")`

Before this fix:
- `os.getenv("OPENROUTER_API_KEY")` returned `<missing>`

After this fix:
- `os.getenv("OPENROUTER_API_KEY")` returns `from-hermes-home`

## Fix

Replace the raw dotenv import-time loading with Hermes' shared env loader:

- use `load_hermes_dotenv(...)`
- load from `HERMES_HOME/.env` first
- keep the repo `.env` as a development fallback

This keeps the change local to `trajectory_compressor.py` and aligns it with Hermes' standard configuration behavior without introducing any refactor, new abstraction, or architectural change.

## Test Evidence

Added a regression test:

- `test_import_loads_env_from_hermes_home`

This test verifies that importing the module correctly loads `OPENROUTER_API_KEY` from `HERMES_HOME/.env`.

Command run:

```bash
python -m pytest tests/test_trajectory_compressor.py -q